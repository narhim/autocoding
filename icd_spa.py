import preprocessing
import myparser

from typing import List, Optional
import warnings
import tempfile #Generate tenporary files and directories
import re
import json
from zipfile import ZipFile
from pathlib import Path
import requests
import untangle
import pandas as pd
import networkx as nx


import math


import os
import random
from collections import defaultdict, Counter
import string
#from sklearn.preprocessing import MultiLabelBinarizer
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import argparse
import itertools
#import numpy as np
#from sklearn.preprocessing import normalize
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
import pickle as pkl

from bs4 import BeautifulSoup
from collections import defaultdict

#import pandas as pd

def add_edges(dataframe,G,list1,list2):
    for c in list1:
        for n,t in enumerate(list2):
            if n < (len(list2)-1):
                if (dataframe[dataframe["codigo"]==c[0]].index.values > dataframe[dataframe["codigo"]==t[0]].index.values) and (dataframe[dataframe["codigo"]==c[0]].index.values < dataframe[dataframe["codigo"]==list2[n+1][0]].index.values):
                    G.add_node(c[0],description=c[1])
                    G.add_edge(c[0],t[0])
            else:
                if (dataframe[dataframe["codigo"]==c[0]].index.values > dataframe[dataframe["codigo"]==t[0]].index.values):
                    G.add_node(c[0],description=c[1])
                    G.add_edge(c[0],t[0])
    return G

def main():


    tabs = []
    xls = pd.ExcelFile('cie10_2008_ref.xls')
    df1 = pd.read_excel(xls, '2008')

    d = [(r["codigo"],r["descriptor"]) for i,r in df1.iterrows() if re.match("Tab",r["codigo"]) !=None]
    f = [(r["codigo"],r["descriptor"]) for i,r in df1.iterrows() if re.match('Cap.*',r["codigo"]) !=None] #Chapters, last one tab.M
    g = [(r["codigo"],r["descriptor"]) for i,r in df1.iterrows() if re.match('[A-Z][0-9]+-[A-Z][0-9].*',r["codigo"]) !=None]#Sections Tab.D and Tab.M
    h = [(r["codigo"],r["descriptor"]) for i,r in df1.iterrows() if re.match('[A-Z][0-9]{2}$',r["codigo"]) !=None] #Single codes in Tab.D Ex: U89
    i = [(r["codigo"],r["descriptor"]) for i,r in df1.iterrows() if re.match('[A-Z][0-9]{2}\.[0-9]$',r["codigo"]) !=None] #Single decimal codes in Tab.D Ex: U89.0
    j = [(r["codigo"],r["descriptor"]) for i,r in df1.iterrows() if re.match('[A-Z][0-9]{2}\.[0-9]{2}$',r["codigo"]) !=None] #Double decimal codes in Tab.D Ex: Y34.99
    k = [(r["codigo"],r["descriptor"]) for i,r in df1.iterrows() if re.match('[A-Z][0-9]{4}\/[0-9]$',r["codigo"]) !=None] #Single codes in Tab.M Ex: M9982/1
    root_name = "root"
    G = nx.DiGraph()
    G.add_node(root_name)
    for section in d:
        G.add_node(section[0],description=section[1])
        G.add_edge(section[0], root_name)
    G =add_edges(df1,G,f,d)
    G = add_edges(df1,G,g,f)
    G = add_edges(df1,G,h,g)
    G = add_edges(df1,G,i,h)
    G = add_edges(df1,G,j,i)
    G = add_edges(df1,G,k,g)
    #I= H.to_directed()
    with open("spa_try.json", "w") as file:
        root_node, *_ = nx.topological_sort(G) #Return a list of nodes in topological sort order. A topological sort is a nonunique permutation of the nodes such that an edge from u to v implies that u appears before v in the topological sort order.
        json_dict = {
            "tree": nx.readwrite.json_graph.tree_data(G, root_node), #Returns data in tree format that is suitable for JSON serialization and use in Javascript documents.
            "codes": sorted(f), #Sort the codes
        }
        json.dump(json_dict, file) #Converts j in a proper json format and dumps it into the file f.
    #print(G.edges())
if __name__ == "__main__":
    main()
