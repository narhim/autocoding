
import json
import re
import networkx as nx
import common

class clef2019_hierarchy:
	def __init__(self):
		self.hierarchy_path = "data/hierarchical_data/de/"
		self.hierarchy_file = "icd10gm_2016.json"
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

		return G

	def combine_graphs(self,graph1,graph2):
		''' Method that combines graphs '''
		graph1 = nx.compose(graph2,graph1)
		return graph1


def main():

	gen = clef2019_hierarchy()

	#Train_dev graph
	#train_dev_G = gen.build_graph_dataset("clef2019/","train_dev/anns_train_dev.txt")
#	#common.out_graph(train_dev_G,"data/hierarchical_data/de/clef2019/","clef2019_train_dev")
#
	##Test graph
	#test_G = gen.build_graph_dataset("clef2019/","test/anns_test.txt")
	#common.out_graph(test_G,"data/hierarchical_data/de/clef2019/","clef2019_test")

	dataset_dir = "clef2019/"
	output_dir = "data/hierarchical_data/de/clef2019/"

	args = common.args_parser()

	if args.partition == "train_dev":
		dataset_file = "train_dev/anns_train_dev.txt"
		output_file = "clef2019_train_dev"
	else:
		dataset_file = "test/anns_test.txt"
		output_file = "clef2019_test"

	graph = gen.build_graph_dataset(dataset_dir,dataset_file)
	common.out_graph(graph,output_dir,output_file)

if __name__ == '__main__':

	main()


