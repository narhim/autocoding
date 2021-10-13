#!/bin/bash

python3 benchmark/hierarchies/full/icd-10-gm.py  
python3 benchmark/hierarchies/datasets/clef2019_parser.py --partition "train_dev"
python3 benchmark/hierarchies/datasets/clef2019_parser.py --partition "test"