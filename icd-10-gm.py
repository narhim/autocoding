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


import math

class GermanICD10Hierarchy:

    def __init__(self):
        self.url = "https://www.dimdi.de/static/de/klassifikationen/icd/icd-10-gm/kode-suche/htmlgm2016/"
        self.build_tree()
        self.link_nodes()
        self.hier_data_path = 'data/hierarchical_data/de/'
        if not os.path.exists(self.hier_data_path):
            os.mkdir(self.hier_data_path)
        #if not os.path.exists(os.path.join(self.hier_data_path, 'icd10hierarchy.txt')):
        self.parse_icd10()
        self.build_graph()

    def build_tree(self):
        rget = requests.get(self.url)
        soup = BeautifulSoup(rget.text, "lxml")
        chapters = soup.findAll("div", {"class": "Chapter"})
        self.tree = dict()
        self.code2title = dict()
        self.dict_sections = {}
        self.dict_links = {}

        def recurse_chapter_tree(chapter_elem):
            ul = chapter_elem.find("ul")
            codes = {}

            if ul is not None:
                # get direct child only
                ul = ul.find_all(recursive=False)
                for uli in ul:
                    uli_codes = recurse_chapter_tree(uli)
                    codes[uli.a.text] = {
                        # "title": uli.a["title"],
                        "subgroups": uli_codes if uli_codes else None
                    }
                    self.dict_sections[uli.a.text] = uli.a["title"]
                    self.dict_links[uli.a.text] = uli.a["href"]
                    # self.code2title[uli.a.text] = uli.a["title"]
            return codes

        # used to clean chapter titles
        prefix_re = re.compile(r"Kapitel (?P<chapnum>[IVX]{1,5})")  # I->minlen, XVIII->maxlen

        for chapter in chapters:
            # chapter code and title
            chap_h2 = chapter.find("h2").text[:-9]
            chap_code = chap_h2.strip("()")
            chap_title = prefix_re.sub("", chap_h2)
            chap_num = prefix_re.search(chap_h2).groupdict()['chapnum']
            if chap_num == "XIXV":
                # small fix for "XIXVerletzungen .." V is part of word
                chap_num = "XIX"
            # parse hierarchy
            self.tree[chap_num] = {
                # "title": chap_title,
                # "code": chap_code,
                "subgroups": recurse_chapter_tree(chapter)
            }
            self.code2title[chap_num] = chap_title
        #print(self.code2title) #'I': 'Bestimmte infektiöse und parasitäre Krankheiten'
        #print(self.tree)

    def link_nodes(self):
        self.parent2childs = dict()

        def set_parent2childs(d):
            for k, v in d.items():
                if k not in ("subgroups"):
                    if v["subgroups"] is not None:
                        self.parent2childs[k] = set(v["subgroups"].keys())
                        set_parent2childs(v["subgroups"])

        set_parent2childs(self.tree)
        def update_parent2childs():
            parent2childs = copy.deepcopy(self.parent2childs)

            def get_all_descendants(parent, childs):
                temp_childs = copy.deepcopy(childs)
                for childi in temp_childs:
                    # get child's childs
                    if childi in parent2childs:
                        # recurse till leaf nodes
                        get_all_descendants(childi, parent2childs[childi])
                        parent2childs[parent].update(parent2childs[childi])

            for parent, childs in self.parent2childs.items():
                get_all_descendants(parent, childs)

            self.parent2childs = parent2childs

        update_parent2childs()

        # get reversed mapping
        self.child2parents = defaultdict(set)

        for parent, childs in self.parent2childs.items():
            for childi in childs:
                self.child2parents[childi].add(parent)


    def rebuild_tree(self):
        hier = self.tree
        tree = defaultdict(list)
        def recursively_fill_dict(icd10tree):
            parents = icd10tree.keys()
            for parent in parents:
                children = icd10tree[parent]['subgroups']
                if children is not None:
                    tree[parent] = list(children.keys())
                    recursively_fill_dict(children)
        recursively_fill_dict(hier)
        return tree

    def parse_icd10(self):
        tree = self.rebuild_tree()
        tree['root'] = list(self.tree.keys())
        save(tree, os.path.join(self.hier_data_path, 'parent2children_tree.p'))
        child2parent_dict = {}
        for parent, children in tree.items():
            for child in children:
                child2parent_dict[child] = parent
        save(child2parent_dict, os.path.join(self.hier_data_path, 'child2parent.p'))

        all_codes = set(tree.keys()).union(set([i for j in tree.values() for i in j]))
        idx2code = {i: code for i, code in enumerate(all_codes)}
        code2idx = {v: k for k, v in idx2code.items()}

        with open(os.path.join(self.hier_data_path, 'icd10hierarchy.txt'), 'w') as f:
            for parent, children in tree.items():
                for child in children:
                    f.write(str(code2idx[parent]) + ' ' + str(code2idx[child]) + '\n')
        save(idx2code, os.path.join(self.hier_data_path, 'idx2icd10.p'))
        save(code2idx, os.path.join(self.hier_data_path, 'icd102idx.p'))


    def get_single_codes(self):
        out_sections = []
        for k,v in self.tree.items():
            l = list(v.values())
            for li in l:
                for section,subsection in li.items():
                    if subsection['subgroups'] != None:
                        out_sections.append(section)
                        #try:
                        for sub,value in subsection.items():
                            for s,v in value.items():
                                #print(type(v.values()))
                                #if v.values() != [None]:
                                    #print(v.values())
                                for f,t in v.items():
                                    if t != None:
                                        out_sections.append(s)

        for out in out_sections:
            self.dict_links.pop(out)

        self.dict_sect_single = {}

        category1 = re.compile("[A-Z][0-9]{2}$") #U80
        category2 = re.compile("[A-Z][0-9]{2}\.[0-9]$") #U80.0
        category3 = re.compile("[A-Z][0-9]{2}\.[0-9]{2}$") #U80.00
        node_cat1 = " "
        node_cat2 = " "
        node_cat3 = " "

        for key,value in self.dict_links.items():                                 
            url = "https://www.dimdi.de/static/de/klassifikationen/icd/icd-10-gm/kode-suche/htmlgm2016/" + value

            rget = requests.get(url)
            soup = BeautifulSoup(rget.text, "lxml")
            w = soup.findAll("a", {"class": "code"})
            y = soup.findAll("span", {"class": "label"})#BUG: already here the encoding disappears, don't know why.

            S = nx.DiGraph()
            section = key
            S.add_node(section)

            for s,z in zip(w,y):
                #single_codes.append((s["id"],z.text)) # U81 \n U82 \n U82.0
                if re.match(category1,s["id"]):
                    node_cat1 = s["id"]
                    S.add_node(node_cat1,description = z.text)
                    S.add_edge(section,node_cat1)
                elif re.match(category2,s["id"]):
                    node_cat2 = s["id"]
                    S.add_node(node_cat2,description = z.text)
                    S.add_edge(node_cat1,node_cat2)
                else:
                    node_cat3 = s["id"]
                    S.add_node(node_cat3,description = z.text)
                    S.add_edge(node_cat2,node_cat3)
            
            self.dict_sect_single[key] = S

    def build_graph(self):
        '''Method to build a hierarchicl graph of all the chapters, 
        sections and codes with their descriptions 
        from the trees build previously'''

        self.get_single_codes() #Runs the method to get the specific codes for each section (category1, category2...).
        chap_list = []
        for k in self.code2title.keys():
            chap_list.append((k,{"title":self.code2title[k]})) #Transform de code2title dict into a list of tuples to build the graph more easily.
        #Initialize the graph    
        G = nx.DiGraph()
        root_name = "root"
        G.add_node(root_name)
        G.add_nodes_from(chap_list) # Get nodes with attributes from chap_list
        for pair in chap_list:
            G.add_edge(root_name,pair[0])
        for k,v in self.tree.items():
            l = list(v.values())
            for li in l:
                for section,subsection in li.items():
                    G.add_node(section,title=self.dict_sections[section])
                    G.add_edge(k,section)
                    if subsection['subgroups'] != None:
                        for value in subsection.values():
                            for sub,x in value.items():
                                G.add_node(sub,title=self.dict_sections[sub])
                                G.add_edge(section,sub)
                                if x["subgroups"] != None:
                                    for w in x.values():
                                        for y,z in w.items():
                                            G.add_node(y,title=self.dict_sections[y])
                                            G.add_edge(sub,y)      
        for value in self.dict_sect_single.values():
            G = nx.compose(value,G)
        with open("icd-10-gm.json", "w",encoding='UTF-8') as f:
            j = {"tree":nx.readwrite.json_graph.tree_data(G, root_name)}
            json.dump(j, f,indent=2,ensure_ascii=False)
        # Its important to use binary mode
        dbfile = open('icd-10-gm.p', 'ab') 
        # source, destination
        pickle.dump(j, dbfile)                     
        dbfile.close()

if __name__ == '__main__':
    gen = GermanICD10Hierarchy()
