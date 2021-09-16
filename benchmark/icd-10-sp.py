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
		''' Method to stratify the dictionary of codes based on their patters. Returns lists for each level with code and descriptions.'''
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
				level_1_codes.append(co) #Level 1 doesn't explicitly exist in the excel file, but 
	
		return level_1_codes,level_2_codes,level_3_codes

	def build_graph(self):
		''' Method that builds the hierarchy tree given the dictionary of codes with their description.'''
		level_1_codes,level_2_codes,level_3_codes = self.stratify_codes(self.codes_descriptors_7)
		G  = nx.DiGraph()
		root_name = "root"
		G.add_node(root_name)
		G.add_nodes_from(level_1_codes)
		for code in level_1_codes:
			G.add_edge(root_name,code)
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

class SpaICD10_Prc_Hierarchy():
	def __init__(self):

		url = "https://eciemaps.mscbs.gob.es/ecieMaps/download?name=2018_PROCEDIMIENTOS_CIE10ES_%20NUEVOS_BORRADOS_EDITADOS%20Y%20COMPLETA_20170921_632774861361197060.xlsx"

		
		file, response = urllib.request.urlretrieve(url)
		xls = pd.ExcelFile(file)
		df1 = pd.read_excel(xls, 'completa',encoding="utf-8")
		print(df1.shape)
		df2 = df1.groupby("codigo")
		for d in df2:
			print(d.shape)
		#self.codes_descriptors = {r["codigo"] : {"full description": r["descripcion"]} for i,r in df1.iterrows()}
		#self.codes_descriptors = [(r["codigo"],{"full description": r["descripcion"]}) for i,r in df1.iterrows()]
		
	def stratify_codes(self,dictionary):
		''' Method to stratify the dictionary of codes based on their patters. Returns lists for each level with code and descriptions.'''
		#nodes = dictionary.keys()
		
		#level_7 = re.compile("([0-9][A-Z][0-9][A-Z][0-9][A-Z]{2})|([A-Z]{3}[0-9]{4})|([0-9]{7})|([0-9]{6}[A-Z])|([0-9]{5}[A-Z][0-9])|([0-9]{3}[A-Z][0-9]{3})|([0-9]{3}[A-Z][0-9][A-Z][0-9])") #0S9C4ZX
		level_7_codes = self.codes_descriptors
		#for code in nodes:
		#	if re.search(level_7,code):
		#	level_7_codes.append((code,dictionary[code]))
				#level_7_codes.append(code)
		level_1_codes = [code[0] for (code,description) in level_7_codes]
		level_2_codes = [code[:2] for (code,description) in level_7_codes]
		level_3_codes = [code[:3] for (code,description) in level_7_codes]
		level_4_codes = [code[:4] for (code,description) in level_7_codes]
		level_5_codes = [code[:5] for (code,description) in level_7_codes]
		level_6_codes = [code[:6] for (code,description) in level_7_codes]
		

		return level_1_codes,level_2_codes,level_3_codes,level_4_codes,level_5_codes,level_6_codes,level_7_codes

	def build_edges(self,graph,level1,level2):

		for code in level1:
			for c in level2:
				if c.find(code):
					graph.add_edge(code,c)

		return graph

	def build_graph(self):
		''' Method that builds the hierarchy tree given the dictionary of codes with their description.'''
		#level_1_codes,level_2_codes,level_3_codes,level_4_codes,level_5_codes,level_6_codes,level_7_codes = self.stratify_codes(self.codes_descriptors)
		G  = nx.DiGraph()
		root_name = "root"
		G.add_node(root_name)
		#G.add_nodes_from(level_1_codes)
		#for code in level_1_codes:
		#	G.add_edge(root_name,code)
		

		

		#G.add_nodes_from(level_2_codes)
		#G = self.build_edges(G,level_1_codes,level_2_codes)
		


		#G.add_nodes_from(level_7_codes)
		#for code in level_6_codes:
		#	for (c,d) in level_7_codes:
		#		if re.match(code,c):
		#			G.add_edge(code,c)
		#lost = []
		#for (node,descr) in level_7_codes:
		#	if len(list(nx.all_simple_paths(G, source="root", target=node))) == 0:
		#		lost.append(node)
		#	#for path in nx.all_simple_paths(G, source="root", target=node):
		#   	#	print(path)
		#print(lost)
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
	icd_o_spa = SpaICD_O_Hierarchy()
	G1_icd_o_spa = icd_o_spa.build_graph()
	write_output(G1_icd_o_spa,"icd-o-sp")
	#icd_diag_spa = SpaICD10_Prc_Hierarchy()
	#G_icd_diag_spa = icd_diag_spa.build_graph()
	#write_output(G_icd_diag_spa,"icd-diag-sp")
if __name__ == '__main__':
	main()
