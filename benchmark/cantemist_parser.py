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
		'''Methods that gets the codes for a specific dataset.'''

		codes = set()
		with open(dataset_path + file) as f:
			codes = set(l.split('\t')[1] for l in f.read().splitlines()[1:])
		return codes

	def norm_codes(self,dataset_path):
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
		self.hierarchy_path = "data/hierarchical_data/sp/"
		self.hierarchy_file = "icd-o-sp.json"
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
		self.subsections = []
		for chapter in self.chapters:
			for section in list(self.H.neighbors(chapter)):
				self.sections.append(section)
		for section in self.sections:
			for subsection in list(self.H.neighbors(section)):
				self.subsections.append(subsection)



	def build_graph_dataset(self,codes):
		'''Method that builds a directed graph for the dataset specificied, also returns codes for possible comparison purposes.'''
		
		G = self.H
		for subsection in self.subsections:
			if (subsection not in codes) and (subsection in list(G.nodes())):
				G.remove_node(subsection)

		for section in self.sections:
			if section in list(G.nodes()):
				if section not in codes and len(list(G.neighbors(section))) == 0:
					G.remove_node(section)

		for node in list(G.nodes()):
			if node not in codes:
				if len(list(G.neighbors(node))) == 0:
					G.remove_node(node)
		codes_not_in_H = []
		for code in codes:
			if code not in list(G.nodes()):
				codes_not_in_H.append(code)
		return G,codes_not_in_H

	def combine_graphs(self,graph1,graph2):
		''' Method that combines graphs '''
		graph1 = nx.compose(graph2,graph1)
		return graph1

	def out_graph(self,graph,out_path,out_file):
		''' Method that saves a directed graph in a json and a pickle file. '''
		#Specific to graph
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
	with open(out_path + out_file, "w",encoding='UTF-8') as f:
		f.write("Codes not in hierarchy from task " + task + "\n")
		for code in list_codes:
			f.write(code + "\n")



if __name__ == '__main__':


	gen = cantemist_hierarchy()
	codes = cantemist_codes()

	#Train, dev and test for coding task.
	train_codes = codes.coding_codes("cantemist/train-set/cantemist-coding/","train-coding.tsv")
	train_G,train_codes_not_in_H = gen.build_graph_dataset(train_codes)
	gen.out_graph(train_G,"data/hierarchical_data/sp/cantemist/","cantemist-train-coding")

	dev1_codes = codes.coding_codes("cantemist/dev-set1/cantemist-coding/","dev1-coding.tsv")
	dev1_G, dev1_codes_not_in_H = gen.build_graph_dataset(dev1_codes)
	gen.out_graph(dev1_G,"data/hierarchical_data/sp/cantemist/","cantemist-dev1-coding")

	dev2_codes = codes.coding_codes("cantemist/dev-set2/cantemist-coding/","dev2-coding.tsv")
	dev2_G,dev2_codes_not_in_H = gen.build_graph_dataset(dev2_codes)
	gen.out_graph(dev2_G,"data/hierarchical_data/sp/cantemist/","cantemist-dev2-coding")

	test_codes = codes.coding_codes("cantemist/test-set/cantemist-coding/","test-coding.tsv")
	test_G, test_codes_not_in_H = gen.build_graph_dataset(test_codes)
	gen.out_graph(test_G,"data/hierarchical_data/sp/cantemist/","cantemist-test-coding")

	codes_not_in_H = train_codes_not_in_H + dev1_codes_not_in_H + dev2_codes_not_in_H + test_codes_not_in_H
	codes_not_in_H = set(codes_not_in_H)
	write_list(codes_not_in_H,"coding","data/hierarchical_data/sp/cantemist/","cantemist-coding-not-in-h.txt")

	#Train, dev and test for norm task.
	train_norm_codes = codes.norm_codes("cantemist/train-set/cantemist-norm/")
	train_norm_G,train_norm_codes_not_in_H = gen.build_graph_dataset(train_norm_codes)
	gen.out_graph(train_norm_G,"data/hierarchical_data/sp/cantemist/","cantemist-train-norm")

	dev1_norm_codes = codes.norm_codes("cantemist/dev-set1/cantemist-norm/")
	dev1_norm_G,dev1_norm_codes_not_in_H = gen.build_graph_dataset(dev1_norm_codes)
	gen.out_graph(dev1_norm_G,"data/hierarchical_data/sp/cantemist/","cantemist-dev1-norm")

	dev2_norm_codes = codes.norm_codes("cantemist/dev-set2/cantemist-norm/")
	dev2_norm_G,dev2_norm_codes_not_in_H = gen.build_graph_dataset(dev2_norm_codes)
	gen.out_graph(dev2_norm_G,"data/hierarchical_data/sp/cantemist/","cantemist-dev2-norm")

	test_norm_codes = codes.norm_codes("cantemist/test-set/cantemist-norm/")
	test_norm_G,test_norm_codes_not_in_H = gen.build_graph_dataset(test_norm_codes)
	gen.out_graph(train_norm_G,"data/hierarchical_data/sp/cantemist/","cantemist-test-norm")

	codes_not_in_H = train_norm_codes_not_in_H + dev1_norm_codes_not_in_H + dev2_norm_codes_not_in_H + test_norm_codes_not_in_H
	codes_not_in_H = set(codes_not_in_H)
	write_list(codes_not_in_H,"norm","data/hierarchical_data/sp/cantemist/","cantemist-norm-not-in-h.txt")