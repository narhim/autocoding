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


class SpaICOHierarchy():
	def __init__(self):

		url = "https://eciemaps.mscbs.gob.es/ecieMaps/download?name=2018_CIEO31_TABLA_%20REFERENCIA_con_6_7_caracteres_final_20180111_5375350050755186721_7033700654037542595.xlsx"
		output_dir = "data/hierarchical_data/sp/"
		if not os.path.exists(output_dir):
			os.makedirs(output_dir)
		
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

def write_output(G,f_name):
	''' Methods that writes the resulting graph both in a json and a pickle file. '''
	dir_name = "data/hierarchical_data/sp/"
	with open(dir_name + f_name + ".json", "w",encoding='UTF-8') as f:
	    root_node, *_ = nx.topological_sort(G)
	    j = {"tree":nx.readwrite.json_graph.tree_data(G, root_node)}
	    json.dump(j, f,indent=2,ensure_ascii=False)
	dbfile = open(dir_name + f_name + '.p', 'ab') 
	pickle.dump(j, dbfile)                     
	dbfile.close()


def main():
	icd_o_spa = SpaICOHierarchy()
	G1_icd_o_spa = icd_o_spa.build_graph()
	write_output(G1_icd_o_spa,"icd-o-sp")

if __name__ == '__main__':
	main()
