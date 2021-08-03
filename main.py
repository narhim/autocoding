import preprocessing

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


def main():

    #Obtain ICD hierarchies.
    G_icd10cm_2019, codes_icd10cm_2019 = preprocessing.build_icd10_hierarchy_from_url(
        "https://www.cms.gov/Medicare/Coding/ICD10/Downloads/2019-ICD-10-CM-Code-Descriptions.zip",
        "https://www.cms.gov/Medicare/Coding/ICD10/Downloads/2019-ICD-10-CM-Tables-and-Index.zip",
    )
    #For the moment we don't need this, but might in the future.
    #G_icd10cm_2020, codes_icd10cm_2020 = build_icd10_hierarchy_from_url(
    #    "https://www.cms.gov/Medicare/Coding/ICD10/Downloads/2020-ICD-10-CM-Codes.zip",
    #    "https://www.cms.gov/Medicare/Coding/ICD10/Downloads/2020-ICD-10-CM-Code-Tables.zip",
    #)
    #G_icd10cm_2021, codes_icd10cm_2021 = build_icd10_hierarchy_from_url(
    #    "https://www.cms.gov/files/zip/2021-code-descriptions-tabular-order.zip",
    #    "https://www.cms.gov/files/zip/2021-code-tables-and-index.zip",
    #)
    outdir = Path("icdcodex/data")
    for G, codes, fname in [
        (G_icd10cm_2019, codes_icd10cm_2019, "icd-10-2019-hierarchy.json",),
        #(G_icd10cm_2020, codes_icd10cm_2020, "icd-10-2020-hierarchy.json",),
        #(G_icd10cm_2021, codes_icd10cm_2021, "icd-10-2021-hierarchy.json",),
    ]:
        with open(outdir / fname, "w") as f:
            root_node, *_ = nx.topological_sort(G) #Return a list of nodes in topological sort order. A topological sort is a nonunique permutation of the nodes such that an edge from u to v implies that u appears before v in the topological sort order.
            j = {
                "tree": nx.readwrite.json_graph.tree_data(G, root_node), #Returns data in tree format that is suitable for JSON serialization and use in Javascript documents.
                "codes": sorted(codes), #Sort the codes
            }
            json.dump(j, f) #Converts j in a proper json format and dumps it into the file f.


    #Obtain codes from train/dev split
    codes = set()
    with open('clef2019/train_dev/anns_train_dev.txt') as f:
        codes = codes.union(set('|'.join([l.split('\t')[-1] for l in f.read().splitlines()[1:]]).split('|')))
    codes = {c for c in codes if c}


if __name__ == "__main__":
    main()
