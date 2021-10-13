import pickle
import json
import os
import networkx as nx
import argparse

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

def out_graphs(graph_diag,graph_proc,out_path,out_file):
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

def args_parser(argv=None):
    """
    Parse command line arguments
    :param argv:
    :return:
    """
    parser = argparse.ArgumentParser(description="Preprocess Data")
    parser.add_argument(
        "--partition",
        default="test",
        type=str,
        help="Select partition of dataset",
        required=True
    )
    parser.add_argument(
        "--task",
        default="x",
        type=str,
        help="Select task of dataset",
        required=False
    )
    return parser.parse_args(argv)
