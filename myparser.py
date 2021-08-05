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


class ICDHierarchy():
    def __init__(self, args):
        self.args = args
        self.dataset = args.data_dir.split('/')[1]
        #self.extant_hierarchy = 'data/hierarchical_data/icd-10-2019-hierarchy.json'
        # from https://github.com/icd-codex/icd-codex/blob/dev/icdcodex/data/icd-10-2019-hierarchy.json
        self.hier_data_path = ''

    def get_dataset_codes(self):
        """
        Loads in all codes from the actual relevant dataset from the data split .tsv files
        :return:
        """
        codes = set()
        for t in ['train', 'dev']:
            with open(os.path.join(self.args.data_dir, '{}_{}_{}.tsv'.format(t, self.args.label_threshold,
                                                                             self.args.ignore_labelless_docs))) as f:
                codes = codes.union(set('|'.join([l.split('\t')[-1] for l in f.read().splitlines()[1:]]).split('|')))
        codes = {c for c in codes if c}
        return codes

    def get_all_codes(self):
        """
        Loads in all codes in their hierarchy from the file containing the codes and their descriptions
        :return:
        """
        with open(os.path.join(self.args.data_dir, 'desc.tsv')) as f:
            codes = set([d.split('\t')[0] for d in f.readlines()])
        return codes

    def build_tree(self):
        """
        Builds a tree from our dataset
        :return:
        """
        all_codes = sorted(self.get_all_codes())
        all_codes = [c for c in all_codes if '-' not in c]
        print("Building ICD10 Hierarchy Tree...")
        for i, code1 in enumerate(tqdm(all_codes)):
            is_parent = True
            while is_parent:
                for code2 in all_codes[i + 1:]:
                    if len(code1) < len(code2) and code1 == code2[:len(code1)]:
                        self.tree[code1].append(code2)
                    else:
                        is_parent = False
                        break
                if i + 1 == len(all_codes) or code2 == all_codes[-1]:
                    break

    def load_extant_hier(self):
        hier = json.load(open(self.extant_hierarchy))['tree']
        return hier

    def build_extant_hier(self):
        hier = self.load_extant_hier()

        def recursively_fill_dict(icd10tree):
            parent = icd10tree['id'].lower()
            if '(' in parent and ')' in parent:
                parent = parent[parent.find("(") + 1:parent.find(")")]
            try:
                children = icd10tree['children']
                for children_dict in children:
                    child = children_dict['id'].lower()
                    if '(' in child and ')' in child:
                        child = child[child.find("(") + 1:child.find(")")]
                    self.external_tree[parent.lower()].append(child)
                    recursively_fill_dict(children_dict)
            except:
                pass

        recursively_fill_dict(hier)

    def fill_final_tree(self, tree):
        for parent, children in tree.items():
            for child in children:
                if self.full_child2parent_dict[child]:
                    parent_already_there = self.full_child2parent_dict[child][0]
                    true_parent = [parent_already_there, parent][np.argmax([len(parent_already_there), len(parent)])]
                    self.full_child2parent_dict[child] = [true_parent]
                else:
                    self.full_child2parent_dict[child].append(parent)
            self.full_parent2children_tree[parent] += children

    def merge_trees(self):
        self.fill_final_tree(self.tree)
        self.fill_final_tree(self.external_tree)

    def parse_icd10(self, parse_own=True):
        self.build_tree()
        self.build_extant_hier()
        self.merge_trees()
        all_codes = set(self.full_child2parent_dict.keys()).union(
            set(i[0] for i in self.full_child2parent_dict.values()))
        all_codes = sorted(all_codes)
        idx2code = {i: code for i, code in enumerate(all_codes)}
        code2idx = {v: k for k, v in idx2code.items()}
        with open(os.path.join(self.hier_data_path, 'icd10hierarchy.txt'), 'w') as f:
            for child, parent in self.full_child2parent_dict.items():
                f.write(str(code2idx[parent[0]]) + ' ' + str(code2idx[child]) + '\n')
        save(idx2code, os.path.join(self.hier_data_path, 'idx2icd10.p'))
        save(code2idx, os.path.join(self.hier_data_path, 'icd102idx.p'))
        try:
            assert self.get_dataset_codes().issubset(set(all_codes))
        except:
            print("The following codes from the dataset are not in the hierarchy:")
            print(set(self.get_dataset_codes()) - set(all_codes))

class GermanICD10Hierarchy:

    def __init__(self):
        self.url = "https://www.dimdi.de/static/de/klassifikationen/icd/icd-10-gm/kode-suche/htmlgm2016/" #Ger ICD 10
        self.build_tree() #After this, we have 2 dictionaries: tree, with all the ICD ger codes, and codes2title, with the descriptions of each section in ger ICD10
        self.link_nodes() #After, dictionary of par to child.
        self.hier_data_path = 'data/hierarchical_data/de/'
        #self.args = args
        if not os.path.exists(self.hier_data_path):
            os.makedirs(self.hier_data_path)
        if not os.path.exists(os.path.join(self.hier_data_path, 'icd10hierarchy.txt')):
            self.parse_icd10()

    def build_tree(self):
        rget = requests.get(self.url)
        soup = BeautifulSoup(rget.text, "lxml")
        chapters = soup.findAll("div", {"class": "Chapter"})
        self.tree = dict()
        self.code2title = dict()

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


    def link_nodes(self):
        self.parent2childs = dict()
#
        def set_parent2childs(d):
            for k, v in d.items():
                if k not in ("subgroups"):
                    if v["subgroups"] is not None:
                        self.parent2childs[k] = set(v["subgroups"].keys())
                        set_parent2childs(v["subgroups"])
#
        set_parent2childs(self.tree)
        
        def update_parent2childs():
            parent2childs = copy.deepcopy(self.parent2childs)
#
            def get_all_descendants(parent, childs):
                temp_childs = copy.deepcopy(childs)
                for childi in temp_childs:
                    # get child's childs
                    if childi in parent2childs:
                        # recurse till leaf nodes
                        get_all_descendants(childi, parent2childs[childi])
                        parent2childs[parent].update(parent2childs[childi])
#
            for parent, childs in self.parent2childs.items():
                get_all_descendants(parent, childs)

            self.parent2childs = parent2childs

        update_parent2childs()

        # get reversed mapping
        self.child2parents = defaultdict(set)
#
        for parent, childs in self.parent2childs.items():
            for childi in childs:
                self.child2parents[childi].add(parent)

    def get_dataset_codes(self):
        """
        Loads in all codes from the actual relevant dataset from the data split .tsv files
        :return:
        """
        codes = set()
        for t in ['train', 'dev']:
            with open('clef2019/train_dev/anns_train_dev.txt') as f:
                codes = codes.union(set('|'.join([l.split('\t')[-1] for l in f.read().splitlines()[1:]]).split('|')))
        codes = {c for c in codes if c}
        return codes

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
        #print(tree)
        tree['root'] = list(self.tree.keys())
        #print(tree)
        #save(tree, os.path.join(self.hier_data_path, 'parent2children_tree.p'))
        #child2parent_dict = {}
        #for parent, children in tree.items():
        #    for child in children:
        #        child2parent_dict[child] = parent
        #save(child2parent_dict, os.path.join(self.hier_data_path, 'child2parent.p'))
#
#        #all_codes = set(tree.keys()).union(set([i for j in tree.values() for i in j]))
#        #idx2code = {i: code for i, code in enumerate(all_codes)}
#        #code2idx = {v: k for k, v in idx2code.items()}
#
#        #with open(os.path.join(self.hier_data_path, 'icd10hierarchy.txt'), 'w') as f:
#        #    for parent, children in tree.items():
#        #        for child in children:
#        #            f.write(str(code2idx[parent]) + ' ' + str(code2idx[child]) + '\n')
#        #save(idx2code, os.path.join(self.hier_data_path, 'idx2icd10.p'))
#        #save(code2idx, os.path.join(self.hier_data_path, 'icd102idx.p'))
#        #try:
#        #    assert self.get_dataset_codes().issubset(set(all_codes))
#        #except:
#        #    print("The following codes from the dataset are not in the hierarchy:")
        #    print(set(self.get_dataset_codes()) - set(all_codes))