#!/bin/bash

#Generates full-extent German ICD10 2016 hierarchy and saves it into a pickle file and a json file (it also accepts 2019/2020/2021 versions).
python3 benchmark/hierarchies/full/icd-10-gm.py  
#Generates train_dev cantemist2019 hierarchy from json full-extent hierarchy and saves into json and pickle files: train_dev, test.
python3 benchmark/hierarchies/datasets/clef2019_parser.py --partition "train_dev"
#Generates test cantemist2019 hierarchy from json full-extent hierarchy and saves into json and pickle files: train_dev, test.
python3 benchmark/hierarchies/datasets/clef2019_parser.py --partition "test"