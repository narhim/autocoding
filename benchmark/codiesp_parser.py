#!/usr/bin/env python3

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


def get_codes(dataset_path,file):
		''' Method that get the codes for one subset of the coding task.'''
		codes = set()
		with open(dataset_path + file) as f:
			codes = set(l.split('\t')[1].upper() for l in f.read().splitlines()[:])
		return codes

def get_codes_x(dataset_path,file):
		''' Method that get the codes for one subset of the coding task.'''
		diagnosis = set()
		procedure = set()
		with open(dataset_path + file) as f:
			#codes = set(l.split('\t')[1].upper() 
			for l in f.read().splitlines()[:]:
				columns = l.split('\t')
				if columns[1].upper() == "DIAGNOSTICO":
					diagnosis.add(columns[2].upper())
				else:
					procedure.add(columns[2].upper())
		return diagnosis,procedure


class codiesp_hierarchy:
	def __init__(self,hierarchy_file):
		self.hierarchy_path = "data/hierarchical_data/sp/" #Location of hierarchy
		self.hierarchy_file = hierarchy_file
		self.retrieve_hierarchy_json()
		self.get_chapters_section()

	def retrieve_hierarchy_json(self):
		'''Retrieves the full-extent hierarchy from a json file.'''
		hier = json.load(open(self.hierarchy_path+self.hierarchy_file))['tree']
		self.H = nx.readwrite.json_graph.tree_graph(hier)
		root_node, *_ = nx.topological_sort(self.H)

	def get_chapters_section(self):
		'''Get the chapters, sections and subsections from the hierarchy to later on build the dataset hierarchy.'''
		chapters = list(self.H.neighbors("root"))
		sections = []
		chapter = "Cap"
		self.level_1_codes = [] #A00, Z9A
		self.level_2_codes = [] #A00.0, Y93.H
		self.level_3_codes = [] #A00.00, T53.1X, V99.XX, T80.A9 
		self.level_4_codes = [] #A00.000, T21.71X, T53.0X2, V84.5XX
		self.level_5_codes = [] #A00.00AB, A00.000A, T53.0X1A, V84.5XXA, V99.XXXA, T80.A9XA, R40.2344, R40.A21A
		for node in list(self.H.nodes()):
			if len(node) == 3:
				self.level_1_codes.append(node)
			elif (len(node) == 5):
				self.level_2_codes.append(node)
			elif (len(node) == 6) and (chapter not in node):
				self.level_3_codes.append(node)
			elif len(node) == 7:
				self.level_4_codes.append(node)
			elif len(node) == 8:
				self.level_5_codes.append(node)
			#else:	#Safety check to avoid leaving codes out.
			#	print(node)

	def build_graph_dataset(self,codes):
		'''Method that builds a directed graph for the dataset specificied, also returns a list of the codes in dataset but not in H.'''
		
		G = self.H.copy() #Rename it to be safe.
		for level_5 in self.level_5_codes:
			if (level_5 not in codes) and (level_5 in list(G.nodes())):
				G.remove_node(level_5) #Start by removing final nodes not in dataset.
				#if nx.is_tree(G) == False:
				#	print(level_5)

		for level_4 in self.level_4_codes:
			if level_4 in list(G.nodes()):
				if level_4 not in codes and len(list(G.neighbors(level_4))) == 0:
					G.remove_node(level_4) #Remove intermediate nodes not in dataset and without any children.

		for level_3 in self.level_3_codes:
			if level_3 in list(G.nodes()):
				if level_3 not in codes and len(list(G.neighbors(level_3))) == 0:
					G.remove_node(level_3) #Remove intermediate nodes not in dataset and without any children.

		for level_2 in self.level_2_codes:
			if level_2 in list(G.nodes()):
				if level_2 not in codes and len(list(G.neighbors(level_2))) == 0:
					G.remove_node(level_2) #Remove intermediate nodes not in dataset and without any children.
		for level_1 in self.level_1_codes:
			if level_1 in list(G.nodes()):
				if level_1 not in codes and len(list(G.neighbors(level_1))) == 0:
					G.remove_node(level_1) #Remove intermediate nodes not in dataset and without any children.

		for node in list(G.nodes()):
			if node not in codes:
				if len(list(G.neighbors(node))) == 0:
					G.remove_node(node) #Remove superior nodes not in dataset and with no children.



		codes_not_in_H = []
		for code in codes:
			if code not in list(G.nodes()):
				codes_not_in_H.append(code)

		return G,codes_not_in_H

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

class codiesp_proc_hierarchy:
	def __init__(self,hierarchy_file):
		self.hierarchy_path = "data/hierarchical_data/sp/" #Location of hierarchy
		self.hierarchy_file = hierarchy_file
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
		self.level_1_codes = [] #A00, Z9A
		self.level_2_codes = [] #A00.0, Y93.H
		self.level_3_codes = [] #A00.00, T53.1X, V99.XX, T80.A9 
		self.level_4_codes = [] #A00.000, T21.71X, T53.0X2, V84.5XX
		self.level_5_codes = [] #A00.00AB, A00.000A, T53.0X1A, V84.5XXA, V99.XXXA, T80.A9XA, R40.2344, R40.A21A
		#print(self.H.adj())
		for node in list(self.H.nodes()):
			if len(node) == 2:
				self.sections.append(node)
			elif len(node) == 3:
				self.level_1_codes.append(node)
			elif len(node) == 4:
				self.level_2_codes.append(node)
			elif (len(node) == 5):
				self.level_3_codes.append(node)
			elif (len(node) == 6):
				self.level_4_codes.append(node)
			elif (len(node) == 7) and ("-" not in node):
				self.level_5_codes.append(node)
			#else:	#Safety check to avoid leaving codes out.
			#	print(node)

	def build_graph_dataset(self,codes):
		'''Method that builds a directed graph for the dataset specificied, also returns a list of the codes in dataset but not in H.'''
		
		G = self.H.copy() #Rename it to be safe.
		#print(self.level_5_codes)
		for level_5 in self.level_5_codes:
			if (level_5 not in codes):
				G.remove_node(level_5) #Remove intermediate nodes not in dataset and without any children.
#
		for level_4 in self.level_4_codes:
			#if level_4 in list(G.nodes()):
			if level_4 not in codes and len(list(G.neighbors(level_4))) == 0:
				G.remove_node(level_4) #Remove intermediate nodes not in dataset and without any children.

		for level_3 in self.level_3_codes:
			#if level_3 in list(G.nodes()):
			if level_3 not in codes and len(list(G.neighbors(level_3))) == 0:
				G.remove_node(level_3) #Remove intermediate nodes not in dataset and without any children.

		for level_2 in self.level_2_codes:
			#if level_2 in list(G.nodes()):
			if level_2 not in codes and len(list(G.neighbors(level_2))) == 0:
				G.remove_node(level_2) #Remove intermediate nodes not in dataset and without any children.
		for level_1 in self.level_1_codes:
			#if level_1 in list(G.nodes()):
			if level_1 not in codes and len(list(G.neighbors(level_1))) == 0:
				G.remove_node(level_1) #Remove intermediate nodes not in dataset and without any children.
		for section in self.sections:
			#if section in list(G.nodes()):
			if section not in codes and len(list(G.neighbors(section))) == 0:
				G.remove_node(section) #Remove intermediate nodes not in dataset and without any children.
		for chapter in self.chapters:
			#if chapter in list(G.nodes()):
			if chapter not in codes and len(list(G.neighbors(chapter))) == 0:
				G.remove_node(chapter) #Remove intermediate nodes not in dataset and without any children.

		codes_not_in_H = []
		for code in codes:
			if code not in list(G.nodes()):
				codes_not_in_H.append(code)

		return G,codes_not_in_H

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
def combine_graphs(HD,HP):
	#HD = nx.relabel_nodes(HD, {"root":"root diagnosis"})
	#HP = nx.relabel_nodes(HP, {"root":"root procedures"})
	#G = nx.disjoint_union(HD,HP)
	G  = nx.DiGraph()
	#root_name = "main root"
	#G.add_node(root_name)
	#G.add_nodes_from(HD)
	##G.add_edges_from(list(HD.edges()))
	#G.add_edge(root_name,"root diagnosis")
	##G.add_nodes_from(HP)
	##G.add_edges_from(list(HP.edges()))
	#G.add_edge(root_name,"root procedures")
	#for node in list(G.nodes()):
	#	print(G.in_edges(node))
	G.add_edges_from(HD.edges(data=True))
	G.add_edges_from(HP.edges(data=True))
	G.add_nodes_from(HD.nodes(data=True))
	G.add_nodes_from(HP.nodes(data=True))
	return G

def out_graph(graph,out_path,out_file):
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

def main():
	#DIAGNOSIS
	#Get the hierarchy
	diag = codiesp_hierarchy("icd-diag-sp.json")
	#Get the codes
	codiesp_path = "codiesp/final_dataset_v4_to_publish/"
	#train_diag_codes = get_codes(codiesp_path,"train/trainD.tsv")
	#train_diag_G,train_diag_not_in_H = diag.build_graph_dataset(train_diag_codes)
	#diag.out_graph(train_diag_G,"data/hierarchical_data/sp/codiesp/","codiesp-train-diag")

	#dev_diag_codes = get_codes(codiesp_path,"dev/devD.tsv")
	#dev_diag_G,dev_diag_not_in_H = diag.build_graph_dataset(dev_diag_codes)
	#diag.out_graph(dev_diag_G,"data/hierarchical_data/sp/codiesp/","codiesp-dev-diag")
	
	#test_diag_codes = get_codes(codiesp_path,"test/testD.tsv")
	#test_diag_G,test_diag_not_in_H = diag.build_graph_dataset(test_diag_codes)
	#diag.out_graph(test_diag_G,"data/hierarchical_data/sp/codiesp/","codiesp-test-diag")

	proc = codiesp_proc_hierarchy("icd-proc-sp.json")
	#train_proc_codes = get_codes(codiesp_path,"train/trainP.tsv")
	#train_proc_G,train_proc_not_in_H = proc.build_graph_dataset(train_proc_codes)
	#proc.out_graph(train_proc_G,"data/hierarchical_data/sp/codiesp/","codiesp-train-proc")
	#
	#dev_proc_codes = get_codes(codiesp_path,"dev/devP.tsv")
	#dev_proc_G,dev_proc_not_in_H = proc.build_graph_dataset(dev_proc_codes)
	#proc.out_graph(dev_proc_G,"data/hierarchical_data/sp/codiesp/","codiesp-dev-proc")	
#
#	#test_proc_codes = get_codes(codiesp_path,"test/testP.tsv")
#	#test_proc_G,test_proc_not_in_H = proc.build_graph_dataset(test_proc_codes)
	#proc.out_graph(test_proc_G,"data/hierarchical_data/sp/codiesp/","codiesp-test-proc")

	train_x_diag,train_x_proc = get_codes_x(codiesp_path,"train/trainX.tsv")
	train_x_diag_G,train_x_diag_not_in_H = diag.build_graph_dataset(train_x_diag)
	train_x_proc_G,train_x_proc_not_in_H = proc.build_graph_dataset(train_x_proc)
	with open("data/hierarchical_data/sp/codiesp/"+"codiesp-train-x" + ".json", "w",encoding='UTF-8') as f:
	    root_node, *_ = nx.topological_sort(train_x_diag_G)
	    root_node_2,*_ = nx.topological_sort(train_x_proc_G)
	    j = {"tree diagnosis":nx.readwrite.json_graph.tree_data(train_x_diag_G, root_node),"tree procedures":nx.readwrite.json_graph.tree_data(train_x_proc_G, root_node)}
	    json.dump(j, f,indent=2,ensure_ascii=False)
	dev_x_diag,dev_x_proc = get_codes_x(codiesp_path,"dev/devX.tsv")
	dev_x_diag_G,dev_x_diag_not_in_H = diag.build_graph_dataset(dev_x_diag)
	dev_x_proc_G,dev_x_proc_not_in_H = proc.build_graph_dataset(dev_x_proc)
	with open("data/hierarchical_data/sp/codiesp/"+"codiesp-dev-x" + ".json", "w",encoding='UTF-8') as f:
	    root_node, *_ = nx.topological_sort(dev_x_diag_G)
	    root_node_2,*_ = nx.topological_sort(dev_x_proc_G)
	    j = {"tree diagnosis":nx.readwrite.json_graph.tree_data(dev_x_diag_G, root_node),"tree procedures":nx.readwrite.json_graph.tree_data(dev_x_proc_G, root_node)}
	    json.dump(j, f,indent=2,ensure_ascii=False)


	test_x_diag,test_x_proc = get_codes_x(codiesp_path,"test/testX.tsv")
	test_x_diag_G,test_x_diag_not_in_H = diag.build_graph_dataset(test_x_diag)
	test_x_proc_G,test_x_proc_not_in_H = proc.build_graph_dataset(test_x_proc)
	with open("data/hierarchical_data/sp/codiesp/"+"codiesp-test-x" + ".json", "w",encoding='UTF-8') as f:
	    root_node, *_ = nx.topological_sort(test_x_diag_G)
	    root_node_2,*_ = nx.topological_sort(test_x_proc_G)
	    j = {"tree diagnosis":nx.readwrite.json_graph.tree_data(test_x_diag_G, root_node),"tree procedures":nx.readwrite.json_graph.tree_data(test_x_proc_G, root_node)}
	    json.dump(j, f,indent=2,ensure_ascii=False)



if __name__ == '__main__':
	main()