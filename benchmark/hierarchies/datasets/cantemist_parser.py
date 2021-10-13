import os
import pickle
import re
import json
import networkx as nx
import common

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
					for level_2 in list(self.H.neighbors(level_1)):
						self.level_2.append(level_2)

	def build_graph_dataset(self,codes):
		'''Method that builds a directed graph for the dataset specificied, also returns a list of the codes in dataset but not in H.'''
		def add_nd_codes(G,par,child):
			'''Add codes with no description to graph. '''
			G.add_node(child)
			G.add_edge(par,child)
			attrs = {child:{"full description": "no hay descripción", "short description": "ND"}}
			nx.set_node_attributes(G,attrs)

			return G
		def build_descriptions(G,par,child):
			'''Builds descriptions for six digits codes. Dictionaries obtained from manual.'''
			#Dictionaries with descriptions for sixth digit. Needed to add codes in dataset but not in hierarchy.
			full_sixth_digit = {"1":"grado I, bien diferenciado","2":"grado II, moderadamente diferenciado","3":"grado III, pobremente diferenciado","4":"grado IV, indiferenciado","5":"´célula T","6":"célula B","7":"célula nula","8":"célula NK","9":"no se ha determinado el grado o la célula"}
			short_sixth_digit = {"1":"G1","2":"G2","3":"G3","4":"G4","5":"´célula T","6":"célula B","7":"célula nula","8":"célula NK","9":"GSD"}
			
			dict_attrs = G.nodes()[par]

			full_str_to_add =full_sixth_digit[child[-1]]
			short_str_to_add = short_sixth_digit[child[-1]]

			full_old = dict_attrs["full description"]
			short_old = dict_attrs["short description"]
				
			full_str = full_old + " - " + full_str_to_add
			short_str = short_old + " - " + short_str_to_add
			node = {child : {"full description": full_str, "short description": short_str}}

			return node
		
		G = self.H.copy() #Rename it to be safe.
		
		for subsection in self.level_2:
			if (subsection not in codes) and (subsection in list(G.nodes())):
				G.remove_node(subsection) #Start by removing final nodes not in dataset.


		for section in self.level_1:
			if section in list(G.nodes()):
				if section not in codes and len(list(G.neighbors(section))) == 0:
					G.remove_node(section) #Remove intermediate nodes not in dataset and without any children.

		for node in list(G.nodes()):
			if node not in codes:
				if len(list(G.neighbors(node))) == 0:
					G.remove_node(node) #Remove superior nodes not in dataset and with no children.

		codes_not_in_H = set(code for code in codes if code not in list(G.nodes())) #Set of codes in dataset but not in hierarchy.

		#Add codes in dataset and not in hierarchy. Examples of shape of codes in comments
		for code in codes_not_in_H:
			if "H" in code:#9735/6/H and 9735/66/H
				c = code[:-2]
				if c in list(G.nodes):
					G = add_nd_codes(G,c,code)
				elif c in list(self.H.nodes()):
					parent = list(self.H.predecessors(c))[0]
					if parent not in list(G.nodes()):	
						grandparent = list(self.H.predecessors(parent))[0]
						G = add_nd_codes(G,grandparent,parent)
					G = add_nd_codes(G,parent,code)
				else:
					co = code[:-3]
					if (co not in list(G.nodes())) and (co in list(self.H.nodes())): #8815/11/H
						cod = code[:-5]
						G = add_nd_codes(G,cod,co)
					elif code[:-4] in list(self.H.nodes()):
						if code[:-4] not in list(G.nodes()):
							parent = list(self.H.predecessors(code[:-4]))[0]
							G = add_nd_codes(G,parent,code[:-4])
						G = add_nd_codes(G,code[:-4],co)
					elif code[:-5] in list(self.H.nodes()):#8011/11/H
						G = add_nd_codes(G,code[:-5],co)

					G = add_nd_codes(G,co,c)
					G = add_nd_codes(G,c,code)

			elif (re.match("^[0-9]{4}/[0-9]{2}$",code)):#9080/63
				c = code[:-1]
				if c in list(G.nodes()):
					node = build_descriptions(G,c,code)
					G.add_node(code)
					nx.set_node_attributes(G,node)
					G.add_edge(c,code)
										
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

					node = build_descriptions(G,c,code)
					G.add_node(code)
					nx.set_node_attributes(G,node)
					G.add_edge(c,code)
				else:
					if code[:-3] in list(G.nodes()):
						G = add_nd_codes(G,code[:-3],code[:-1])

					elif code[:-3] in list(self.H.nodes()):
						parent = list(self.H.predecessors(code[:-3]))[0]
						G = add_nd_codes(G,parent,code[:-3])
						G = add_nd_codes(G,code[:-3],code[:-1])
					G = add_nd_codes(G,code[:-1],code)
			elif len(code) == 6:#9735/6
				c = code[:-2]
				if c not in list(G.nodes()):
					parent = list(self.H.predecessors(c))[0]
					G = add_nd_codes(G,parent,c)
					G = add_nd_codes(G,c,code)
				elif (c in list(G.nodes())) and (code not in list(G.nodes())):
					G = add_nd_codes(G,c,code)


		#codes_not_in_H = set(code for code in codes_not_in_H if code not in list(G.nodes())) #Security check to ensure that all codes have benn added.

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



def main():
	gen = cantemist_hierarchy()
	codes = cantemist_codes()

	output_directory = "data/hierarchical_data/sp/cantemist/"

	args = common.args_parser()
	
	if ("1" in args.partition) or ("2" in args.partition):
		name = args.partition[0:3]+ "-set" + args.partition[-1]
	else:
		name = args.partition + "-set"
	source_directory = "cantemist/" + name + "/cantemist-" + args.task + "/" 
	output_file = "cantemist-" + args.partition + "-" + args.task

	if args.task == "coding":
		source_file = args.partition + "-" + args.task + ".tsv"
		set_codes = codes.coding_codes(source_directory,source_file)
	else:
		set_codes = codes.norm_codes(source_directory)
	hierarchy = gen.build_graph_dataset(set_codes)
	common.out_graph(hierarchy,output_directory,output_file)

	
	
if __name__ == '__main__':
	main()