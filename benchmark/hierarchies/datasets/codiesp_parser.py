#!/usr/bin/env python3

import os
import pickle
import re
import json
import networkx as nx
import common

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
		not_in_5 = [level_5 for level_5 in self.level_5_codes if (level_5 not in codes) and (level_5 in list(G.nodes()))]
		for l in not_in_5:
			G.remove_node(l)#Start by removing final nodes not in dataset.

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
		return G

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
		for level_5 in self.level_5_codes:
			if (level_5 not in codes):
				G.remove_node(level_5)#Remove intermediate nodes not in dataset and without any children.
		
		for level_4 in self.level_4_codes:
			if level_4 not in codes and len(list(G.neighbors(level_4))) == 0:
				G.remove_node(level_4) #Remove intermediate nodes not in dataset and without any children.

		for level_3 in self.level_3_codes:
			if level_3 not in codes and len(list(G.neighbors(level_3))) == 0:
				G.remove_node(level_3) #Remove intermediate nodes not in dataset and without any children.

		for level_2 in self.level_2_codes:
			if level_2 not in codes and len(list(G.neighbors(level_2))) == 0:
				G.remove_node(level_2) #Remove intermediate nodes not in dataset and without any children.
		for level_1 in self.level_1_codes:
			if level_1 not in codes and len(list(G.neighbors(level_1))) == 0:
				G.remove_node(level_1) #Remove intermediate nodes not in dataset and without any children.
		for section in self.sections:
			if section not in codes and len(list(G.neighbors(section))) == 0:
				G.remove_node(section) #Remove intermediate nodes not in dataset and without any children.
		for chapter in self.chapters:
			if chapter not in codes and len(list(G.neighbors(chapter))) == 0:
				G.remove_node(chapter) #Remove intermediate nodes not in dataset and without any children.

		return G

class write_graph:

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

	def out_graphs(self,graph_diag,graph_proc,out_path,out_file):
		''' Method that saves a directed graph in a json and a pickle file. '''
		if not os.path.exists(out_path):
			os.makedirs(out_path)
		with open(out_path + out_file + ".json", "w",encoding='UTF-8') as f:
		    root_node, *_ = nx.topological_sort(graph_diag)
		    root_node_2,*_ = nx.topological_sort(graph_proc)
		    j = {"tree diagnosis":nx.readwrite.json_graph.tree_data(graph_diag,root_node),"tree procedures":nx.readwrite.json_graph.tree_data(graph_proc, root_node)}
		    json.dump(j, f,indent=2,ensure_ascii=False)
		#Save final graph in a pickle file.
		dbfile = open(out_path + out_file + '.p', 'ab') 
		pickle.dump(j, dbfile)                     
		dbfile.close()

def main():
	#Get the hierarchies
	diag = codiesp_hierarchy("icd-diag-sp.json")
	proc = codiesp_proc_hierarchy("icd-proc-sp.json")

	codiesp_path = "codiesp/final_dataset_v4_to_publish/"
	output_path = "data/hierarchical_data/sp/codiesp/"

	args = common.args_parser()

	if args.task == "diagnosis":
		set_codes = get_codes(codiesp_path,args.partition + "/" + args.partition + "D.tsv")
		graph = diag.build_graph_dataset(set_codes)
		common.out_graph(graph,output_path,"codiesp-" + args.partition + "-diag")
	elif args.task == "procedures":
		set_codes = get_codes(codiesp_path,args.partition + "/" + args.partition + "P.tsv")
		graph = proc.build_graph_dataset(set_codes)
		common.out_graph(graph,output_path,"codiesp-" + args.partition + "-proc")
	else:
		diag_set_codes,proc_set_codes = get_codes_x(codiesp_path,args.partition + "/" + args.partition + "X.tsv")
		graph_diag = diag.build_graph_dataset(diag_set_codes)
		graph_proc = proc.build_graph_dataset(proc_set_codes)
		common.out_graphs(graph_diag,graph_proc,output_path,"codiesp-" + args.partition + "-x")


if __name__ == '__main__':
	main()