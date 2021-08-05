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


def main():

    #Obtain ICD hierarchies.
    G_icd10cm_2019, codes_icd10cm_2019 = preprocessing.build_icd10_hierarchy_from_url(
        "https://www.cms.gov/Medicare/Coding/ICD10/Downloads/2019-ICD-10-CM-Code-Descriptions.zip",
        "https://www.cms.gov/Medicare/Coding/ICD10/Downloads/2019-ICD-10-CM-Tables-and-Index.zip",
    )
    #G_icd10cm_2019, codes_icd10cm_2019 = preprocessing.build_icd10_hierarchy_from_url(
    #    "https://www.openagrar.de/servlets/MCRFileNodeServlet/openagrar_derivate_00019621/nts-icd.zip"
    #    "https://www.openagrar.de/servlets/MCRFileNodeServlet/openagrar_derivate_00021578/nts_icd.zip"
    #)
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

    clef = myparser.GermanICD10Hierarchy() #ger ICD10 codes in dict_tree and dict_par2child
    clef_codes = clef.get_dataset_codes() #clefcodes
    de_icd_10_tree = clef.rebuild_tree() #clef tree
    name = 'clef-icd-10-hierarchy.json'
    x = clef.parse_icd10()
    #print(x)
    #root_node, *_ = nx.topological_sort(clef_tree)
    #with open(outdir/name,"w") as f:
    #    #ger_j = {
        #        "tree": nx.readwrite.json_graph.tree_data(clef_tree, root_node), #Returns data in tree format that is suitable for JSON serialization and use in Javascript documents.
        #        "codes": sorted(clef_codes), #Sort the codes
        #    }
        #json.dump(de_icd_10_tree,f)



if __name__ == "__main__":
    main()
