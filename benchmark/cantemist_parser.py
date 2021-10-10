import os
import random
from collections import defaultdict, Counter
import string
from sklearn.preprocessing import MultiLabelBinarizer
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import argparse
import itertools
import numpy as np
from sklearn.preprocessing import normalize
from utils import *
import string
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
import json
from torch import save
import copy
import requests
import re
import os
import pickle as pkl

from bs4 import BeautifulSoup
from collections import defaultdict

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
from networkx.algorithms.traversal.depth_first_search import dfs_tree

import math

class cantemist_codes:

	def coding_codes(self,dataset_path,file):
		''' Method that get the codes for one subset of the coding task.'''

		codes = set()
		with open(dataset_path + file) as f:
			codes = set(l.split('\t')[1] for l in f.read().splitlines()[1:])
		return codes

	def norm_codes(self,dataset_path):
		''' Method that get the codes for one subset of the norm task.'''
		files = []
		for r, d, f in os.walk(dataset_path):
			for file in f:
				if '.ann' in file:
					files.append(os.path.join(r, file))           
		codes = []
		for f in files:
			with open(f,"r",encoding = "utf-8") as file:
				for count, line in enumerate(file, start=1):
					if count % 2 == 0:
						code = line.split("\t")[-1].strip("\n")
						if code not in codes:
							codes.append(code)
		return codes	
		

class cantemist_hierarchy:
	def __init__(self):
		self.hierarchy_path = "data/hierarchical_data/sp/" #Location of hierarchy
		self.hierarchy_file = "icd-o-sp.json" #Name of hierarchy
		self.retrieve_hierarchy_json()
		self.get_chapters_section()

	def retrieve_hierarchy_json(self):
		'''Retrieves the full-extent hierarchy from a json file.'''
		hier = json.load(open(self.hierarchy_path+self.hierarchy_file))['tree']
		self.H = nx.readwrite.json_graph.tree_graph(hier)
		root_node, *_ = nx.topological_sort(self.H)


	def get_chapters_section(self):
		'''Get the chapters, sections and subsections from the hierarchy to later on build the dataset hierarchy.'''
		self.chapters = list(self.H.neighbors("root"))
		self.sections = []
		self.level_1 = []
		self.level_2 = []
		for chapter in self.chapters:
			for section in list(self.H.neighbors(chapter)):
				for level_1 in list(self.H.neighbors(section)):
					self.level_1.append(level_1)
		#for level_1 in self.level_1:
					for level_2 in list(self.H.neighbors(level_1)):
						self.level_2.append(level_2)
		



	def build_graph_dataset(self,codes):
		'''Method that builds a directed graph for the dataset specificied, also returns a list of the codes in dataset but not in H.'''
		
		G = self.H.copy() #Rename it to be safe.
		
		for subsection in self.level_2:
			if (subsection not in codes) and (subsection in list(G.nodes())):
				G.remove_node(subsection) #Start by removing final nodes not in dataset.


		for section in self.level_1:
			if section in list(G.nodes()):
				if section not in codes and len(list(G.neighbors(section))) == 0:
					G.remove_node(section) #Remove intermediate nodes not in dataset and without any children.
					#if section == "8122/6":
					#	print("PROBLEM")

		for node in list(G.nodes()):
			if node not in codes:
				if len(list(G.neighbors(node))) == 0:
					G.remove_node(node) #Remove superior nodes not in dataset and with no children.

		full_sixth_digit = {"1":"grado I, bien diferenciado","2":"grado II, moderadamente diferenciado","3":"grado III, pobremente diferenciado","4":"grado IV, indiferenciado","5":"´célula T","6":"célula B","7":"célula nula","8":"célula NK","9":"no se ha determinado el grado o la célula"}
		short_sixth_digit = {"1":"G1","2":"G2","3":"G3","4":"G4","5":"´célula T","6":"célula B","7":"célula nula","8":"célula NK","9":"GSD"}

		codes_not_in_H = []
		for code in codes:
			if code not in list(G.nodes()):
				codes_not_in_H.append(code)
		nd_dict = {"full description": "no hay descripción", "short description": "ND"}
		for code in codes_not_in_H:
			if "H" in code:
				c = code[:-2]
				if c in list(G.nodes):
					G.add_node(code) #1111/4
					G.add_edge(c,code)
					attrs = {code:nd_dict}
					nx.set_node_attributes(G,attrs)
				elif c in list(self.H.nodes()):
					parent = list(self.H.predecessors(c))[0]
					if parent not in list(G.nodes()):	
						grandparent = list(self.H.predecessors(parent))[0]
						G.add_node(parent)
						G.add_edge(grandparent,parent)
						attrs = {parent:nd_dict}
						nx.set_node_attributes(G,attrs)
					G.add_node(code)
					G.add_edge(parent,code)
					attrs = {code:nd_dict}
					nx.set_node_attributes(G,attrs)
				else:
					co = code[:-3]
					if (co not in list(G.nodes())) and (co in list(self.H.nodes())): #8815/11/H
						cod = code[:-5]
						G.add_node(co)
						G.add_edge(cod,co)
						attrs = {co:nd_dict}
						nx.set_node_attributes(G,attrs)
						G.add_node(c)
						G.add_edge(co,c)
						attrs = {c:nd_dict}
						nx.set_node_attributes(G,attrs)
						G.add_node(code)
						G.add_edge(c,code)
						attrs = {code:nd_dict}
						nx.set_node_attributes(G,attrs)
					elif code[:-4] in list(self.H.nodes()): #POSSIBLE BUG 8011/1/H
						if code[:-4] not in list(G.nodes()):
							parent = list(self.H.predecessors(code[:-4]))[0]
							G.add_node(code[:-4])
							G.add_edge(parent,code[:-4])
							attrs = {code[:-4]:nd_dict}
							nx.set_node_attributes(G,attrs)
						G.add_node(co)
						G.add_edge(code[:-4],co)
						attrs = {co:nd_dict}
						nx.set_node_attributes(G,attrs)
						G.add_node(c)
						G.add_edge(co,c)
						attrs = {c:nd_dict}
						nx.set_node_attributes(G,attrs)
						G.add_node(code)
						G.add_edge(c,code)
						attrs = {code:nd_dict}
						nx.set_node_attributes(G,attrs)
					elif code[:-5] in list(self.H.nodes()):#8011/11/H
						G.add_node(co)
						G.add_edge(code[:-5],co)
						attrs = {co:nd_dict}
						nx.set_node_attributes(G,attrs)
						G.add_node(c)
						G.add_edge(co,c)
						attrs = {c:nd_dict}
						nx.set_node_attributes(G,attrs)
						G.add_node(code)
						G.add_edge(c,code)
						attrs = {code:nd_dict}
						nx.set_node_attributes(G,attrs)
				#attrs = {code:nd_dict}
				#nx.set_node_attributes(G,attrs)
			elif (re.match("^[0-9]{4}/[0-9]{2}$",code)):
				c = code[:-1]
				if c in list(G.nodes()):#9080/63
					#try: #TEMPORARY
					dict_attrs = G.nodes()[c]

					full_str_to_add =full_sixth_digit[code[-1]]
					short_str_to_add = short_sixth_digit[code[-1]]

					full_old = dict_attrs["full description"]
					short_old = dict_attrs["short description"]
				
					full_str = full_old + " - " + full_str_to_add
					short_str = short_old + " - " + short_str_to_add
					node = {code : {"full description": full_str, "short description": short_str}}
					
					G.add_node(code)
					nx.set_node_attributes(G,node)
					G.add_edge(c,code)
					#except:
					#	G.add_node(code)
					#	nx.set_node_attributes(G,node)
					#	G.add_edge(c,code)
										
				elif c in list(self.H.nodes):
					co = code[:-3]
					dict_attrs = self.H.nodes()[c]
					node = {c:dict_attrs}
					
					if co not in list(G.nodes()):
						G.add_node(co)
						parent = list(self.H.predecessors(co))[0]
						G.add_edge(parent,co)
						G.add_node(c)
						nx.set_node_attributes(G,node)
						G.add_edge(co,c)
					else:
						G.add_node(c)
						nx.set_node_attributes(G,node)
						G.add_edge(co,c)

					dict_attrs = G.nodes()[c]

					full_str_to_add =full_sixth_digit[code[-1]]
					short_str_to_add = short_sixth_digit[code[-1]]

					full_old = dict_attrs["full description"]
					short_old = dict_attrs["short description"]
				
					full_str = full_old + " - " + full_str_to_add
					short_str = short_old + " - " + short_str_to_add
					node = {code : {"full description": full_str, "short description": short_str}}

					G.add_node(code)
					nx.set_node_attributes(G,node)
					G.add_edge(c,code)
				else:
					if code[:-3] in list(G.nodes()):
						G.add_node(code[:-1])
						G.add_edge(code[:-3],code[:-1])
						attrs = {code[:-1]:nd_dict}
						nx.set_node_attributes(G,attrs)
						G.add_node(code)
						G.add_edge(code[:-1],code)
						attrs = {code:nd_dict}
						nx.set_node_attributes(G,attrs)
					elif code[:-3] in list(self.H.nodes()):
						parent = list(self.H.predecessors(code[:-3]))[0]

						G.add_node(code[:-3])
						G.add_edge(parent,code[:-3])
						attrs = {code[:-3]:nd_dict}
						nx.set_node_attributes(G,attrs)
						G.add_node(code[:-1])
						G.add_edge(code[:-3],code[:-1])
						attrs = {code[:-1]:nd_dict}
						nx.set_node_attributes(G,attrs)
						G.add_node(code)
						G.add_edge(code[:-1],code)
						attrs = {code:nd_dict}
						nx.set_node_attributes(G,attrs)
			elif len(code) == 6:#9735/6 #BUG IN THIS SECTION
				c = code[:-2]
				if c not in list(G.nodes()):
					parent = list(self.H.predecessors(c))[0]
					G.add_node(c)
					G.add_edge(parent,c)
					attrs = {c:nd_dict}
					nx.set_node_attributes(G,attrs)
					G.add_node(code)
					G.add_edge(c,code)
					attrs = {code:nd_dict}
					nx.set_node_attributes(G,attrs)
				elif c in list(G.nodes()):
					if code not in list(G.nodes()):
						#print("?????")
						G.add_node(code)
						G.add_edge(c,code)
						attrs = {code:nd_dict}
						nx.set_node_attributes(G,attrs)

		codes_not_in_H = [code for code in codes_not_in_H if code not in list(G.nodes())]

		return G

	def combine_graphs(self,graph1,graph2):
		''' Method that combines graphs '''
		graph1 = nx.compose(graph2,graph1)
		return graph1

	def out_graph(self,graph,out_path,out_file):
		''' Method that saves a directed graph in a json and a pickle file. '''
		if not os.path.exists(out_path):
			os.makedirs(out_path)
		with open(out_path + out_file + ".json", "w",encoding='UTF-8') as f:
		    root_node, *_ = nx.topological_sort(graph)
		    j = {"tree":nx.readwrite.json_graph.tree_data(graph, root_node)}
		    json.dump(j, f,indent=2,ensure_ascii=False)
		#Save final graph in a pickle file.
		dbfile = open(out_path + out_file + '.p', 'ab') 
		pickle.dump(j, dbfile)                     
		dbfile.close()

def write_list(list_codes,task,out_path,out_file):
	'''Function that writes a list in a txt. file, used for unseen codes.'''
	with open(out_path + out_file, "w",encoding='UTF-8') as f:
		f.write("Codes not in hierarchy from task " + task + "\n")
		for code in list_codes:
			f.write(code + "\n")



if __name__ == '__main__':


	gen = cantemist_hierarchy()
	codes = cantemist_codes()

	#Train, dev and test for coding task.
	train_codes = codes.coding_codes("cantemist/train-set/cantemist-coding/","train-coding.tsv")
	train_G = gen.build_graph_dataset(train_codes)
	gen.out_graph(train_G,"data/hierarchical_data/sp/cantemist/","cantemist-train-coding")

	dev1_codes = codes.coding_codes("cantemist/dev-set1/cantemist-coding/","dev1-coding.tsv")
	dev1_G = gen.build_graph_dataset(dev1_codes)
	gen.out_graph(dev1_G,"data/hierarchical_data/sp/cantemist/","cantemist-dev1-coding")

	dev2_codes = codes.coding_codes("cantemist/dev-set2/cantemist-coding/","dev2-coding.tsv")
	dev2_G = gen.build_graph_dataset(dev2_codes)
	gen.out_graph(dev2_G,"data/hierarchical_data/sp/cantemist/","cantemist-dev2-coding")

	test_codes = codes.coding_codes("cantemist/test-set/cantemist-coding/","test-coding.tsv")
	test_G = gen.build_graph_dataset(test_codes)
	gen.out_graph(test_G,"data/hierarchical_data/sp/cantemist/","cantemist-test-coding")
#
#	##Train, dev and test for norm task.
	train_norm_codes = codes.norm_codes("cantemist/train-set/cantemist-norm/")
	train_norm_G = gen.build_graph_dataset(train_norm_codes)
	gen.out_graph(train_norm_G,"data/hierarchical_data/sp/cantemist/","cantemist-train-norm")
#
	dev1_norm_codes = codes.norm_codes("cantemist/dev-set1/cantemist-norm/")
	dev1_norm_G = gen.build_graph_dataset(dev1_norm_codes)
	gen.out_graph(dev1_norm_G,"data/hierarchical_data/sp/cantemist/","cantemist-dev1-norm")
#
	dev2_norm_codes = codes.norm_codes("cantemist/dev-set2/cantemist-norm/")
	dev2_norm_G = gen.build_graph_dataset(dev2_norm_codes)
	gen.out_graph(dev2_norm_G,"data/hierarchical_data/sp/cantemist/","cantemist-dev2-norm")

	test_norm_codes = codes.norm_codes("cantemist/test-set/cantemist-norm/")
	test_norm_G = gen.build_graph_dataset(test_norm_codes)
	gen.out_graph(train_norm_G,"data/hierarchical_data/sp/cantemist/","cantemist-test-norm")
