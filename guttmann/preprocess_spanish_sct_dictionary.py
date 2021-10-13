# -*- coding: utf-8 -*-

import argparse
import logging
import random
import collections
import re
from rdflib import Graph as RDFGraph


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(args):
    # create the RDF graph object
    rg = RDFGraph()
    logger.info(f"  Reading Spanish SNOMED CT RDF file from `{args.path_spanish_sct}` ...")
    rg.parse(args.path_spanish_sct)
    
    concept2text = collections.defaultdict(list)
    
    for item in rg:
        concept_id = str(item[0]).split("_")[-1] # item[0] is like ../path/SCT_93050005
        text = str(item[2]).strip() # item[2] is concept description
        # ignore URIs
        if text.startswith("http:"):
            continue
        concept2text[int(concept_id)].append(text)
    
    # in SCT a concept can have multiple textual descriptions,
    # instead of choosing shortest or longest one, we pick a 
    # random one -- setting seed for reproducibility
    random.seed(args.random_state)
    
    count = 0
    logger.info(f"  Creating output file at `{args.path_output_file}` ...")
    with open(args.path_output_file, "w", encoding="utf-8", errors="ignore") as wf:
        for concept_id, texts in list(concept2text.items()):
            # filter out concepts ending with brackets such as disorder (trastorno) / finding (hallazgo)
            __texts = []
            for text in texts:
                if not re.search(r"\(.*?\)", text):
                    __texts.append(text)
            # for some concepts only bracketed versions might exist
            if not __texts:
                __texts = text
            # now select one concept randomly
            concept_description = random.sample(__texts, 1)[0]
            wf.write(f"{concept_id}\t{concept_description}\n")
            count += 1
    
    logger.info(f"  Found {count} concepts!")


def cl_parser(argv=None):
    """
    Parse command line arguments
    :param argv:
    :return:
    """
    parser = argparse.ArgumentParser(description="Parse Spanish SNOMED CT RDF file to simple tab separated file.")
    parser.add_argument("--path_spanish_sct", type=str, help="Path to SCT dictionary (.. DFKI/DICTIONARY/SPANISH/*.rdf)")
    parser.add_argument("--path_output_file", type=str, help="Path to output file (.tsv)")
    parser.add_argument("--random_state", type=int, default=35)
    
    return parser.parse_args(argv)


if __name__=="__main__":
    args = cl_parser()
    main(args)

