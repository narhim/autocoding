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

class clef2019_hierarchy:
	def __init__(self,hierarchy_dir,hierarchy_file):
		self.hierarchy_path = hierarchy_dir
		self.hierarchy_file = hierarchy_file
		self.retrieve_hierarchy_json()
		self.get_chapters_section()

	def retrieve_hierarchy_json(self):
		'''Retrieves the full-extent hierarchy from a json file.'''
		hier = json.load(open(self.hierarchy_path+self.hierarchy_file))['tree']
		self.H = nx.readwrite.json_graph.tree_graph(hier)
		root_node, *_ = nx.topological_sort(self.H)

	def get_chapters_section(self):
		'''Get the chapters and sections from the hierarchy to later on build the dataset hierarchy (dataset only has chapters and sections).'''
		self.chapters = list(self.H.neighbors("root"))
		self.sections = []
		for chapter in self.chapters:
			self.sections.append(list(self.H.neighbors(chapter)))

	def get_codes(self,dataset_path,file):
		'''Methods that gets the codes for a specific dataset.'''

		codes = set()
		with open(dataset_path + file) as f:
		    codes = codes.union(set('|'.join([l.split('\t')[-1] for l in f.read().splitlines()[1:]]).split('|')))
		    return codes

	def build_nodes(self,dataset_path,file):
		''' Methods that builds the nodes as list of tuples (node_name,attribute) to later compose the graph.'''

		codes = self.get_codes(dataset_path,file)
		tuple_chapters = []
		for chapter in self.chapters:
			if chapter in codes:
				tuple_chapters.append((chapter,{"description":self.H.nodes[chapter]["description"]}))
		in_sections = []

		for list_sections in self.sections:
			for section in list_sections:
				if section in codes:
					in_sections.append(section)
		
		tuple_section = []
		for list_s in self.sections:
			nodes_sections = []
			for section in list_s:
				if section in in_sections:
					nodes_sections.append((section,{"description":self.H.nodes[section]["description"]}))
			tuple_section.append(nodes_sections)
		return codes,tuple_chapters,tuple_section

	def build_graph_dataset(self,dataset_path,file):
		'''Method that builds a directed graph for the dataset specificied, also returns codes for possible comparison purposes.'''
		
		codes,tuple_chapters,tuple_sections = self.build_nodes(dataset_path,file)

		G = nx.DiGraph()
		root_name = "root"
		G.add_node(root_name)
		G.add_nodes_from(tuple_chapters)
	
		for chapter in tuple_chapters:
			G.add_edge(root_name,chapter[0])
		
		for chapter,section in zip(self.chapters,tuple_sections):
			G.add_nodes_from(section)
			for node in section:
				G.add_edge(chapter,node[0]) #Till here, non-extant hierarchy of clef 2019

		return G,codes

	def combine_graphs(self,graph1,graph2):
		''' Method that combines graphs '''
		graph1 = nx.compose(graph2,graph1)
		return graph1

	def out_graph(self,graph,out_path,out_file):
		''' Method that saves a directed graph in a json and a pickle file. '''
		#Specific to graph
		with open(out_path + out_file + ".json", "w",encoding='UTF-8') as f:
		            root_node, *_ = nx.topological_sort(graph)
		            j = {"tree":nx.readwrite.json_graph.tree_data(graph, root_node)}
		            json.dump(j, f,indent=2,ensure_ascii=False)
		#Save final graph in a pickle file.
		dbfile = open(out_path + out_file + '.p', 'ab') 
		pickle.dump(j, dbfile)                     
		dbfile.close()




#Retrieve hierarchy from pickle file (not working at the moment)
#dict_hierarchy = pickle.load( open( "data/hierarchical_data/de/icd10gm_2019.p", "rb" ) )
#H = nx.readwrite.json_graph.tree_graph(dict_hierarchy,ident='root')
#G = nx.from_dict_of_dicts(dict_hierarchy)



if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument(
	    "--hierarchy_dir",
	    default="data/hierarchical_data/de/",
	    type=str,
	    help="Directory for json hierarchy files",
	)
	parser.add_argument(
	    "--hierarchy_file",
	    default="icd10gm_2016.json",
	    type=str,
	    help="json hierarchy file",
	)
	parser.add_argument(
	    "--dataset_path",
	    default="clef2019/",
	    type=str,
	    help="Directory for dataset files",
	)
	parser.add_argument(
	    "--train_dev_file",
	    default="train_dev/anns_train_dev.txt",
	    type=str,
	    help="train_dev dataset",
	)
	parser.add_argument(
	    "--test_file",
	    default="test/anns_test.txt",
	    type=str,
	    help="test dataset",
	)
	parser.add_argument(
	    "--output_dir",
	    default="data/hierarchical_data/de/",
	    type=str,
	    help="Directory for output files",
	)
	parser.add_argument(
	    "--out_file_train_dev",
	    default="clef2019_train_dev",
	    type=str,
	    help="File name for train_dev dataset hierarchy outputs",
	)
	parser.add_argument(
	    "--out_file_test",
	    default="clef2019_test",
	    type=str,
	    help="File name for test dataset hierarchy outputs",
	)
	parser.add_argument(
	    "--out_file_combine",
	    default="clef2019",
	    type=str,
	    help="File name for dataset hierarchy outputs",
	)

	args = parser.parse_args()

	gen = clef2019_hierarchy(args.hierarchy_dir,args.hierarchy_file)

	#Train_dev graph
	train_dev_G,train_dev_codes = gen.build_graph_dataset(args.dataset_path,args.train_dev_file)
	gen.out_graph(train_dev_G,args.output_dir,args.out_file_train_dev)

	#Test graph
	test_G, test_codes = gen.build_graph_dataset(args.dataset_path,args.test_file)
	gen.out_graph(test_G,args.output_dir,args.out_file_test)
	
	#All graph
	test_train_dev_G = gen.combine_graphs(train_dev_G,test_G)
	gen.out_graph(test_train_dev_G,args.output_dir,args.out_file_combine)



