#!/bin/bash
python3 benchmark/hierarchies/full/icd-10-sp.py
python3 benchmark/hierarchies/datasets/cantemist_parser.py 
python3 benchmark/hierarchies/datasets/codiesp_parser.py