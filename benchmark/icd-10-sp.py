from typing import List, Optional
import warnings
import tempfile
import re
import json
from zipfile import ZipFile
from pathlib import Path
import requests
import untangle
import pandas as pd
import networkx as nx


import math
import pickle
import os
import urllib
import argparse


class SpaICD_O_Hierarchy():
	def __init__(self):

		url = "https://eciemaps.mscbs.gob.es/ecieMaps/download?name=2018_CIEO31_TABLA_%20REFERENCIA_con_6_7_caracteres_final_20180111_5375350050755186721_7033700654037542595.xlsx"
		
		file, response = urllib.request.urlretrieve(url)
		xls = pd.ExcelFile(file)
		df1 = pd.read_excel(xls, 'Morfología con 7º caracter',encoding="utf-8")
		self.codes_descriptors_7 = {r["codigo"] : {"full description": r["Descriptor Completo"], "short description":r["Descriptor Abreviado"]} for i,r in df1.iterrows()}
		
		
	def stratify_codes(self,dictionary):
		''' Method to stratify the dictionary of codes based on their patterns. Returns lists for each level with code and descriptions.'''
		nodes = dictionary.keys()
		
		level_1 = re.compile("[0-9]{4}/") #8000
		level_2 = re.compile("[0-9]/[0-9]$") #8000/0
		
		level_1_codes = []
		level_2_codes = []
		level_3_codes = [] #8000/00
		
		for code in nodes:
			if re.search(level_2,code):
				level_2_codes.append((code,dictionary[code]))
			else:
				level_3_codes.append((code,dictionary[code]))
		
		for code in level_2_codes:
			c = re.search(level_1,code[0])
			co = c.group()
			co = co.strip("/")
			if co not in level_1_codes:
				level_1_codes.append(co) #Level 1 doesn't explicitly exist in the excel file (thus no description), but it was decided to generate since it's  real level.
	
		return level_1_codes,level_2_codes,level_3_codes

	def build_graph(self):
		''' Method that builds the hierarchy tree given the dictionary of codes with their description.'''

		level_1_codes,level_2_codes,level_3_codes = self.stratify_codes(self.codes_descriptors_7) #First stratify the codes

		#Chapters and subchapters are not in the file used, so they are hard-coded here and separated into 2 for readibility (source: https://eciemaps.mscbs.gob.es/ecieMaps/documentation/documentation.html#)
		complex_chapters = [("801-804", {"description":"Neoplasias epiteliales, SAI"}),("805-808", {"description": "Neoplasias de células escamosas"}),("809-811", {"description": "Neoplasias de células basales"}),("812-813", {"description" :"Papilomas y carcinomas de células transicionales"}), ("814-838", {"description": "Adenomas y adenocarcinomas"}),("839-842", {"description": "Neoplasias de anejos y apéndices cutáneos"}),("844-849", {"description": "Neoplasias quísticas, mucinosas y serosas"}),("850-854", {"description": "Neoplasias ductales y lobulares"}),("856-857", {"description": "Neoplasias epiteliales complejas"}),("859-867", {"description": "Neoplasias especializadas de las gónadas"}),("868-871", {"description": "Paragangliomas y tumores glómicos"}),("872-879", {"description":"Nevus y melanomas"}),
		("881-883", {"description" :"Neoplasias fibromatosas"}),("885-888", {"description":"Neoplasias lipomatosas"}),("889-892", {"description" :"Neoplasias miomatosas"}),
		("893-899", {"description":"Neoplasias complejas mixtas y del estroma"}),("900-903", {"description":"Neoplasias fi broepiteliales"}),("906-909", {"description":"Neoplasias de células germinales"}),
		("912-916", {"description":"Neoplasias de vasos sanguíneos"}),("918-924", {"description":"Neoplasias óseas y condromatosas"}),("927-934", {"description":"Tumores odontogénicos"}),("935-937", {"description":"Tumores misceláneos"}),
		("938-948", {"description":"Gliomas"}),("949-952", {"description":"Neoplasias neuroepiteliomatosas"}),("954-957", {"description":"Tumores de las vainas nerviosas"}),("965-966", {"description":"Linfoma de Hodgkin"}),("967-972", {"description":"Linfomas no Hodgkin"}),("980-994", {"description":"Leucemias"}),("995-996", {"description":"Trastornos mieloproliferativos crónicos"}),("998-999", {"description":"Síndromes mielodisplásicos"})]
		simple_chapters = [("800", {"description" : "Neoplasias, SAI"}),("843", {"description": "Neoplasias mucoepidermoides"}),("855", {"description": "Neoplasias de células acinosas"}), 
		("858", {"description": "Neoplasias epiteliales del timo"}),("880", {"description":"Tumores y sarcomas de tejidos blandos, SAI"}),("884", {"description":"Neoplasias mixomatosas"}),
		("904", {"description":"Neoplasias semejantes a las sinoviales"}),("905", {"description":"Neoplasias mesoteliales"}),("910", {"description":"Neoplasias trofoblásticas"}),
		("911", {"description":"Mesonefromas"}),("917", {"description":"Neoplasias de vasos linfáticos"}),("925", {"description":"Neoplasias de células gigantes"}),("926", {"description":"Tumores óseos misceláneos"}),
		("953", {"description":"Meningiomas"}),("958", {"description":"Tumores de células granulares y sarcomas alveolares de partes blandas"}),("959", {"description":"Linfomas malignos, SAI o difusos"}),("972", {"description":"Linfoma linfoblástico de células precursoras"}),
		("973", {"description":"Tumores de células plasmáticas"}),("974", {"description":"Tumores de mastocitos"}),("975", {"description":"Neoplasias de histiocitos y células linfoides accesorias"}),
		("976",{"description": "Enfermedades inmunoproliferativas"}),("997", {"description": "Otros trastornos hematológicos"})]
		chapters = complex_chapters + simple_chapters #Join back chapters
		subchapters =[("967-969", {"description":"Linfomas de células B maduras"}),("970-971", {"description": "Linfomas de células T maduras y NK"}),
		("980", {"description":"Leucemias, SAI"}),("981-983", {"description":"Leucemias linfoides"}),("984-993", {"description":"Leucemias mieloides"}),
		("994", {"description": "Otras leucemias"})]

		list_chapters = []
		for (chapter,description) in chapters:
			if len(chapter) > 3:
				limits = chapter.split("-")
				start = int(limits[0])
				end = int(limits[1]) + 1
				children = [str(number) for number in range(start,end)]
				list_chapters.append(children)
			else:
				list_chapters.append(chapter)
		G  = nx.DiGraph()
		root_name = "root"
		G.add_node(root_name)
		G.add_nodes_from(chapters)
		for (chapter,description) in chapters:
			G.add_edge(root_name,chapter)

		G.add_nodes_from(subchapters)
		for (subchapter,descrition) in subchapters:
			lookup = subchapter.split("-")[0]
			for chaps in list_chapters:
				if type(chaps) == list:
					if lookup in chaps:
						node = chaps[0] + "-" + chaps[-1]
						G.add_edge(node,subchapter)
		list_subchapters = []
		for (subchapter,description) in subchapters:
			if len(subchapter) > 3:
				limits = subchapter.split("-")
				start = int(limits[0])
				end = int(limits[1]) + 1
				children = [str(number) for number in range(start,end)]
				list_subchapters.append(children)
			else:
				list_subchapters.append(chapter)
		#G.add_nodes_from(level_1_codes)
		for code in level_1_codes:
			parent = code[:-1]
			for subchaps in list_subchapters: #First lookup for subchpters children
				if type(subchaps) == list:
					if parent in subchaps:
						node = subchaps[0] + "-" + subchaps[-1]
						G.add_node(code)
						G.add_edge(node,code)
				else:
					if parent == subchaps:
						G.add_node(code)
						G.add_edge(subchaps,code)
			for chaps in list_chapters: 
				if type(chaps) == list:
					if (parent in chaps) and (code not in list(G.nodes())):
						node = chaps[0] + "-" + chaps[-1]
						G.add_node(code)
						G.add_edge(node,code)
				else:
					if (parent == chaps) and (code not in list(G.nodes())):
						G.add_node(code)
						G.add_edge(chaps,code)

		G.add_nodes_from(level_2_codes)
		for code in level_1_codes:
			for c in level_2_codes:
				if re.match(code,c[0]):
					G.add_edge(code,c[0])

		G.add_nodes_from(level_3_codes)
		for code in level_2_codes:
			for c in level_3_codes:
				if re.match(code[0],c[0]):
					G.add_edge(code[0],c[0])
		return G

class SpaICD10_Diag_Hierarchy():
	def __init__(self):

		url = "https://eciemaps.mscbs.gob.es/ecieMaps/download?name=2018_DIAGNOSTICOS_CIE10ES_REFERENCIA%20Y%20VALIDACION_20171211_7449731228183628205.xlsx"
		file, response = urllib.request.urlretrieve(url)
		xls = pd.ExcelFile(file)
		df1 = pd.read_excel(xls, 'finales y no finales',encoding="utf-8")
		self.codes_descriptors = {r["codigo"] : {"description": r["descripcion"]} for i,r in df1.iterrows()}
	
	def stratify_codes(self,dictionary):
		''' Method to stratify the dictionary of codes based on their patters. Returns lists for each level with code and descriptions.'''
		nodes = list(dictionary.keys()) #All codes
		
		#Regex to match the different levels of codes.
		chap_reg = re.compile("Cap.") #Cap.01
		#sec_reg = re.compile("([A-Z][0-9]{2}-[A-Z])(([0-9]{2})|[0-9][A-Z])$") #A00-A09 Sections and subsections have the same format, they will separated letter
		sec_reg = re.compile("([A-Z][0-9])(([0-9])|([A-Z]))-([A-Z][0-9])(([0-9])|([A-Z]))$")
		#Lists to store the codes of the different levels. Examples of patterns are provided.
		chapters = [] #Cap.01
		sections = [] #A00-A09
		level_1_codes = {} #A00, Z9A
		level_2_codes = [] #A00.0, Y93.H
		level_3_codes = [] #A00.00, T53.1X, V99.XX, T80.A9 
		level_4_codes = [] #A00.000, T21.71X, T53.0X2, V84.5XX
		level_5_codes = [] #A00.00AB, A00.000A, T53.0X1A, V84.5XXA, V99.XXXA, T80.A9XA, R40.2344, R40.A21A
		
		#Stratify the codes
		for n,node in enumerate(nodes):
			if re.search(chap_reg,node):
				chapters.append((node,dictionary[node]))
			elif re.search(sec_reg,node):
				sections.append((node,dictionary[node]))
			elif len(node) == 3:
				level_1_codes[node] = dictionary[node]
			elif len(node) == 5:
				level_2_codes.append((node,dictionary[node]))
			elif len(node) == 6:
				level_3_codes.append((node,dictionary[node]))
			elif len(node) == 7:
				level_4_codes.append((node,dictionary[node]))
			elif len(node) == 8:
				level_5_codes.append((node,dictionary[node]))
			#else:	#Safety check to avoid leaving codes out.
			#	print(node)

		level_2_codes.remove(("Tab.D",dictionary["Tab.D"]))

		return chapters,sections,level_1_codes,level_2_codes,level_3_codes,level_4_codes,level_5_codes
	
	def add_level(self,G,l1,l2):
		'''Method to add hierarchy levels from level_2 to level_5.'''
		G.add_nodes_from(l2)
		#for (level_1,d) in l1:
		#	for (level_2,description) in l2:
		#		if re.match(level_1,level_2):
		#			G.add_edge(level_1,level_2)

		for (level_2,description) in l2:
			G.add_edge(level_2[:-1],level_2)
		return G

	def del_child_add_child(self,G,children,description,beg,end,section,subsection):
		start = children.index(beg)
		finish = children.index(end) + 1
		del children[start:finish]
		G.add_node(subsection)
		G.add_edge(section,subsection)
		attrs={subsection:description}
		nx.set_node_attributes(G,attrs)
		children.append(subsection)
		return children,G

	def build_graph(self):
		''' Method that builds the hierarchy tree given the dictionary of codes with their description.'''
		chapters,sections,level_1_codes,level_2_codes,level_3_codes,level_4_codes,level_5_codes = self.stratify_codes(self.codes_descriptors)
		G  = nx.DiGraph()
		root_name = "root"
		G.add_node(root_name)
		#Add chapters
		G.add_nodes_from(chapters)
		for (chapter,description) in chapters:
			G.add_edge(root_name,chapter)
		#STRATIFY SECTIONS INTO SECTIONS, SUBSECTIONS AND SUBSUBSECTIONS.
		codes_chap = {}
		for (chapter,description) in chapters:
			descr_value = list(description.values())[0]
			section = descr_value[-8:-1].split("-")
			beg = section[0]
			end = section[1]
			children = []
			for level in level_1_codes.keys():
				if re.match(beg,level): #A00
					children.append(level)
				elif re.match(end,level): #B99
					children.append(level)
				elif beg[0] == end[0]:
					if beg[0] == level[0]:

						try:
							if (int(beg[1:]) < int(level[1:])) and (int(end[1:]) > int(level[1:])):
								children.append(level)
						except:
							if (int(beg[1]) <= int(level[1])) and (int(end[1]) >= int(level[1])):
								children.append(level)
				else:
					if beg[0] == level[0]:
						try:
							if (int(beg[1:]) < int(level[1:])):
								children.append(level)
						except:
							if (int(beg[1]) < int(level[1])):
								children.append(level)
					elif end[0] == level[0]:
						try:
							if int(end[1:]) > int(level[1:]):
								children.append(level)
						except:
							if (int(beg[1]) < int(level[1])):
								children.append(level)
					elif (beg[0]<level[0]) and (level[0]<end[0]):
						children.append(level)
			codes_chap[chapter] = children

		sections_chap = {}
		lista = list(codes_chap.items())

		for chapter,children in lista:
			for (section,description) in sections:
				limits = section.split("-")
				beg = limits[0]
				end = limits[1]
				if (chapter == "Cap.20") and (beg=="Y20") and (end=="Y33"):
					children,G = self.del_child_add_child(G,children,description,"Y21",end,chapter,section)
				elif (beg in children) and (end in children):
					children,G = self.del_child_add_child(G,children,description,beg,end,chapter,section)
			sections_chap[chapter] = children
		subsections = [(section,description) for (section,description) in sections if section not in list(G.nodes())]
		sections = [(section,description) for (section,description) in sections if section in list(G.nodes())]
		subsec_sec = {}
		for (section,description) in sections:

			limits = section.split("-")
			beg = limits[0]
			end = limits[1]
			children = []
			for level in level_1_codes.keys():
				
				if re.match(beg,level): #A00
					children.append(level)
				elif re.match(end,level): #B99
					children.append(level)
				elif beg[0] == end[0]:
					if beg[0] == level[0]:
						
						try:
							if (int(beg[1:]) < int(level[1:])) and (int(end[1:]) > int(level[1:])):
								children.append(level)
						except:
							if (int(beg[1]) < int(level[1])) and (int(end[1]) >int(level[1])):
								children.append(level)
							elif section == "O94-O9A" and (level=="O98" or level=="O99"):
								children.append(level)
							elif section == "Z77-Z99" and level=="Z3A":
								children.append(level)
				else:
					if beg[0] == level[0]:
						try:
							if (int(beg[1:]) < int(level[1:])):
								children.append(level)
						except:
							if (int(beg[1]) < int(level[1])):
								children.append(level)
					elif end[0] == level[0]:
						try:
							if int(end[1:]) > int(level[1:]):
								children.append(level)
						except:
							if (int(beg[1]) < int(level[1])):
								children.append(level)
					elif (beg[0]<level[0]) and (level[0]<end[0]):
						children.append(level)
			subsec_sec[section] = children
		sec_subsec = {}
		
		lista = list(subsec_sec.items())
		for section,children in lista:
			for (subsection,description) in subsections:
				limits = subsection.split("-")
				beg = limits[0]
				end = limits[1]
								
				if (beg in children) and (end in children):
					children,G = self.del_child_add_child(G,children,description,beg,end,section,subsection)
					
			sec_subsec[section] = children
		subsubsections = [(section,description) for (section,description) in subsections if section not in list(G.nodes())]
		G.add_nodes_from(subsubsections)
		parent = "T20-T32"
		for (subsubsection,description) in subsubsections:
			G.add_edge(parent,subsubsection)
		
		level_1_keys = list(level_1_codes.keys())
		for section, children in sec_subsec.items():

			for child in children:
				if len(child) == 3:
					G.add_node(child)
					nx.set_node_attributes(G,{child:level_1_codes[child]})
					G.add_edge(section,child)
				else:
					if len(list(G.neighbors(child))) == 0:
						
						limits = child.split("-")
						beg = level_1_keys.index(limits[0])
						end = level_1_keys.index(limits[1]) + 1
						codes = [(code,level_1_codes[code]) for code in level_1_keys[beg:end]]
						G.add_nodes_from(codes)
						for (c,d) in codes:
							G.add_edge(child,c)
					else:
						for subsubsection in list(G.neighbors(child)):
							limits = subsubsection.split("-")
							beg = level_1_keys.index(limits[0])
							end = level_1_keys.index(limits[1]) + 1
							codes = [(code,level_1_codes[code]) for code in level_1_keys[beg:end]]
							G.add_nodes_from(codes)
							for (c,d) in codes:
								G.add_edge(subsubsection,c)
		G.add_nodes_from(level_2_codes)
		for level_1 in level_1_keys:
			for (level_2,description) in level_2_codes:
				if re.match(level_1,level_2):
					G.add_edge(level_1,level_2)
		
		G = self.add_level(G,level_2_codes,level_3_codes)
		G = self.add_level(G,level_3_codes,level_4_codes)
		G = self.add_level(G,level_4_codes,level_5_codes)
		return G

class SpaICD10_Prc_Hierarchy():
	def __init__(self):

		url = "https://eciemaps.mscbs.gob.es/ecieMaps/download?name=2018_PROCEDIMIENTOS_CIE10ES_%20NUEVOS_BORRADOS_EDITADOS%20Y%20COMPLETA_20170921_632774861361197060.xlsx"

		
		file, response = urllib.request.urlretrieve(url)
		xls = pd.ExcelFile(file)
		df1 = pd.read_excel(xls, 'completa',encoding="utf-8")
		df2 = df1.groupby("codigo")
		self.codes_descriptors = {r["codigo"] : {"description": r["descripcion"]} for i,r in df1.iterrows()}
		#self.codes_descriptors = [(r["codigo"],{"full description": r["descripcion"]}) for i,r in df1.iterrows()]

	def stratify_codes(self,dictionary):

		nodes = dictionary.keys()

		chapters = [("0",{"description":"Médico-Quirúrgica"}),("1",{"description":"Obstetricia"}),("2",{"description":"Colocación"}),("3",{"description":"Administración"}),("4",{"description":"Medición y Monitorización"}),
		("5",{"description":"Asistencia y Soporte Extracorpóreos"}),("6",{"description":"Terapias Extracorpóreas"}),("7",{"description":"Osteopatía"}),("8",{"description":"Otros Procedimientos"}),("9",{"description":"Quiropráctica"}),
		("B",{"description":"Imagen"}),("C",{"description":"Medicina Nuclear"}),("D",{"description":"Radioterapia"}),("F",{"description":"Rehabilitación Física y Audiología Diagnóstica"}),("G",{"description":"Salud Mental"}),("H",{"description":"Tratamiento de Abuso de Sustancias"}),("X",{"description":"Nueva Tecnología"})]
		
		subsect_desc_1 = {"A":{"description": "Sistemas Fisiológicos"},"B":{"description": "Sistema Respiratorio"},"C":{"description": "Dispositivo Permanente"},"D":{"description": "Sistema Gastrointestinal"},"E":{"description": "Sistemas Fisiológicos y Regiones Anatómicas"},
						"F":{"description": "Sistema Hepatobiliar y Páncreas"},"G":{"description": "Sistema Endocrino"},"H":{"description": "Piel y Mama"},"J":{"description": "Tejido Subcutáneo y Fascia"},"K":{"description": "Músculos"},"L":{"description": "Tendones"},"M":{"description": "Bursas y Ligamentos"},
						"N":{"description": "Huesos Cráneo y Cara"},"P":{"description": "Huesos Superiores"},"Q":{"description": "Huesos Inferiores"},"R":{"description": "Articulaciones Superiores"}, "S":{"description": "Articulaciones Inferiores"},
						"T":{"description": "Sistema Urinario"},"U":{"description": "Sistema Reproductor Femenino"},"V":{"description": "Sistema Reproductor Masculino"},"W":{"description": "Regiones anatómicas"},"X":{"description": "Regiones Anatómicas, Extremidades Superiores"},
						"Y":{"description": "Regiones Anatómicas, Extremidades Inferiores"},"Z":{"description": "Ninguno(-a)"},
						"0":{"description": "Sistema Nervioso Central"},"1":{"description": "Sistema Nervioso Periférico"},"2":{"description": "Corazón y Grandes Vasos"},"3":{"description": "Arterias Superiores"},"4":{"description": "Arterias Inferiores"},
						"5":{"description": "Venas Superiores"},"6":{"description": "Venas Inferiores"},"7":{"description": "Sistemas Linfático y Hermático"},"8":{"description": "Ojo"},"9":{"description": "Oído, Nariz,Senos Paranasales"}
						}

		subsect_desc_2 = {"30":{"description": "Circulatorio"},"10": {"description": "Embarazo"},"0W":{"description":"Regiones Anatómicas Generales"},"0C":{"description":"Boca y Garganta"},"B2":{"description":"Corazón"},"C2":{"description":"Corazón"},
						"2Y":{"description":"Orificios Anatómicos"},"B5":{"description": "Venas"},"C5":{"description": "Venas"},"B7":{"description": "Sistema Linfático"},"C7":{"description": "Sistema Linfático"},"D7":{"description": "Sistema Linfático"},"B9":{"description": "Oído, Nariz, Boca y Garganta"},
						"C9":{"description": "Oído, Nariz, Boca y Garganta"},"D9":{"description": "Oído, Nariz, Boca y Garganta"},"BH":{"description": "Piel, Tejido Subcutáneo y Mama"},
						"CH":{"description": "Piel, Tejido Subcutáneo y Mama"},"BL":{"description": "Tejido Comectivo"},"BP":{"description": "Huesos Superiores no Axiales"},"BQ":{"description": "Huesos Inferiores no Axiales"},"BR": {"description": "Esqueleto Axial, Excepto Huesos Craneales y Faciales"},
						"BY":{"description": "Feto y Obstetricia"},"CP":{"description": "Sistema Músculo Esquelético"},"DP":{"description": "Sistema Músculo Esquelético"},"D0":{"description": "Sistema Nervioso Central y Periférico"},"DH":{"description": "Piel"},"DM":{"description": "Mama"},"F0":{"description": "Rehabilitación"},
						"F1":{"description": "Audiología Diagnóstica"},"X2":{"description": "Sistema Cardiovascular"},"XH":{"description": "Piel, Tejido Subcutáneo, Fascia y Mama"},"XN":{"description": "Huesos"},"XR":{"description": "Articulaciones"}
						}
		double_subsect = list(subsect_desc_2.keys())

		subsections = []
		level_1_codes = set()
		level_2_codes = set()
		level_3_codes = set()
		level_4_codes = set()
		level_5_codes = []


		
		for node in nodes:
			level_1_codes.add(node[0:3])
			level_2_codes.add(node[0:4])
			level_3_codes.add(node[0:5])
			level_4_codes.add(node[0:6])
			level_5_codes.append((node[:],dictionary[node]))
			if node[0:2] in double_subsect:
				subsections.append((node[0:2],subsect_desc_2[node[0:2]]))
			else:
				subsections.append((node[0:2],subsect_desc_1[node[1]]))
			


		level_1_codes = sorted(level_1_codes)
		level_2_codes = sorted(level_2_codes)
		level_3_codes = sorted(level_3_codes)
		level_4_codes = sorted(level_4_codes)
		
		return chapters,subsections,level_1_codes,level_2_codes,level_3_codes,level_4_codes,level_5_codes
	
	def build_graph(self):
		''' Method that builds the hierarchy tree given the dictionary of codes with their description.'''
		chapters,subsections,level_1_codes,level_2_codes,level_3_codes,level_4_codes,level_5_codes = self.stratify_codes(self.codes_descriptors)

		dict_sect = {"0": [
							("001-00X",{"description":"Sistema Nervioso Central"}),("012-01X",{"description":"Sistema Nervioso Periférico"}),("021-02Y",{"description":"Corazón y Grandes Vasos"}),("031-03W",{"description":"Arterias Superiores"}),("041-04W",{"description":"Arterias Inferiores"}),
							("051-05W",{"description":"Venas Superiores"}),("061-06W",{"description":"Venas Inferiores"}),("072-07Y",{"description":"Sistemas Linfático y Hemático"}),("080-08X",{"description":"Ojo"}),("090-09W",{"description":"Oído, Nariz, Senos Paranasales"}),
							("0B1-0BY",{"description":"Sistema Respiratorio"}),("0C0-0CX",{"description":"Boca y Garganta"}),("0D1-0DY",{"description":"Sistema Gastrointestinal"}),("0F1-0FY",{"description":"Sistema Hepatobiliar y Páncreas"}),("0G2-0GW",{"description":"Sistema Endocrino"}),
							("0H0-0HX",{"description":"Piel y Mama"}),("0J0-0JX",{"description":"Tejido Subcutáneo y Fascia"}),("0K2-0KX",{"description":"Músculos"}),("0L2-0LX",{"description":"Tendones"}),("0M2-0MX",{"description":"Bursas y Ligamentos"}),("0N2-0NW",{"description":"Huesos Cráneo y Cara"}),
							("0P2-0PW",{"description":"Huesos Superiores"}),("0Q2-0QW",{"description":"Huesos Inferiores"}),("0R2-0RW",{"description":"Articulaciones Superiores"}),("0S2-0SW",{"description":"Articulaciones Inferiores"}),("0T1-0TY",{"description":"Sistema Urinario"}),
							("0U1-0UY",{"description":"Sistema Reproductor Femenino"}),("0V1-0VW",{"description":"Sistema Reproductor Masculino"}),("0W0-0WW",{"description":"Regiones Anatómicas Generales"}),("0X0-0XX",{"description":"Regiones Anatómicas, Extremidades Superiores"}),
							("0Y0-0YW",{"description":"Regiones Anatómicas, Extremidades Inferiores"})
						],
					"1": [("102-10Y",{"description":"Sección Obstetricia"})],
					"2": [("2W0-2Y5",{"description":"Sección Colocación"})],
					"3":[("302-3E1",{"description":"Sección Administración"})],
					"4":[("4A0-4B0",{"description":"Sección Medición y Monitorización"})],
					"5": [("5A0-5A2",{"description": "Sección Asistencia y Soporte Extracorpóreos"})],
					"6":[("6A0-6A9",{"description":"Sección Terapias Extracorpóreas "})],
					"7":[("7W0-7W0",{"description":"Sección Osteopático"})],
					"8":[("8C0-8E0",{"description":"Sección Otros Procedimientos"})],
					"9":[("9WB-9WB",{"description":"Sección Quiropráctica"})],
					"B":[("B00-BY4",{"description":"Sección Imagen"})],
					"C":[("C01-CW7",{"description":"Sección Medicina Nuclear"})],
					"D":[("D00-DWY",{"description":"Sección Radioterapia"})],
					"F":[("F00-F15",{"description":"Sección Rehabilitación Física y Audiología Diagnóstica"})],
					"G":[("GZ1-GZJ",{"description": "Sección Salud Mental"})],
					"H":[("HZ2-HZ9",{"description":"Sección Tratamiento de Abuso de Sustancias"})],
					"X":[("X2A-XW0",{"description":"Sección Nueva Tecnología"})],
					}
		G  = nx.DiGraph()
		root_name = "root"
		G.add_node(root_name)
		G.add_nodes_from(chapters)
		G.add_nodes_from(subsections)
		G.add_nodes_from(level_1_codes)
		G.add_nodes_from(level_2_codes)

		for (chapter,description) in chapters:
			G.add_edge(root_name,chapter)

		list_sections = []
		for chapter,sections in dict_sect.items():
			G.add_nodes_from(sections)
			for (section,description) in sections:
				G.add_edge(chapter,section)
				list_sections.append(section)
			
		for (subsection,description) in subsections:
			for section in list_sections:
				if (section[0]=="0") and (subsection[0]=="0"):
					if section[0:2] == subsection[0:2]:
						G.add_edge(section,subsection)
				elif (section[0]==subsection[0]):
					G.add_edge(section,subsection)

		for level in level_1_codes:
		#	G.add_node(level)
			G.add_edge(level[0:-1],level)

		for level in level_2_codes:
			G.add_edge(level[0:-1],level)

		G.add_nodes_from(level_3_codes)
		for level in level_3_codes:
			G.add_edge(level[0:-1],level)
#
		G.add_nodes_from(level_4_codes)
		for level in level_4_codes:
			G.add_edge(level[0:-1],level)
		G.add_nodes_from(level_5_codes)
		for (level,description) in level_5_codes:
			G.add_edge(level[0:-1],level)

		return G

def write_output(G,f_name):
	''' Function that writes the resulting graph both in a json and a pickle file. '''
	dir_name = "data/hierarchical_data/sp/"
	if not os.path.exists(dir_name):
		os.makedirs(dir_name)
	with open(dir_name + f_name + ".json", "w",encoding='UTF-8') as f:
	    root_node, *_ = nx.topological_sort(G)
	    j = {"tree":nx.readwrite.json_graph.tree_data(G, root_node)}
	    json.dump(j, f,indent=2,ensure_ascii=False)
	dbfile = open(dir_name + f_name + '.p', 'ab') 
	pickle.dump(j, dbfile)                     
	dbfile.close()


def main():

	#Generate ICD-O (or CIE-O) hierarchy
	icd_o_spa = SpaICD_O_Hierarchy()
	G1_icd_o_spa = icd_o_spa.build_graph()
	write_output(G1_icd_o_spa,"icd-o-sp")

	#Generate ICD-Diag (or CIE-Diag) hierarchy
	icd_diag_spa = SpaICD10_Diag_Hierarchy()
	G1_icd_diag_spa = icd_diag_spa.build_graph()
	write_output(G1_icd_diag_spa,"icd-diag-sp")

	icd_proc_spa = SpaICD10_Prc_Hierarchy()
	G1_icd_proc_spa = icd_proc_spa.build_graph()
	write_output(G1_icd_proc_spa,"icd-proc-sp")
	
if __name__ == '__main__':
	main()
