#!/bin/bash

#Generates full-extent German ICD10 2016 hierarchy and saves it into a pickle file and a json file (it also accepts 2019/2020/2021 versions).
python3 benchmark/icd-10-gm.py --url "https://www.dimdi.de/static/de/klassifikationen/icd/icd-10-gm/kode-suche/htmlgm2016/" --output_dir "data/hierarchical_data/de/" --file_name "icd10gm_2016" 
#Generates cantemist2019 hierarchy from json full-extent hierarchy and saves into json and pickle files: train_dev, test, and all. Assumes existance of dataset locally. Hierarchy file must be json.
python3 benchmark/clef2019_parser.py --hierarchy_dir "data/hierarchical_data/de/" --hierarchy_file "icd10gm_2016.json" --dataset_path "clef2019/" --train_dev_file "train_dev/anns_train_dev.txt" --test_file "test/anns_test.txt" --output_dir "data/hierarchical_data/de/" --out_file_train_dev "clef2019_train_dev" --out_file_test "clef2019_test"  --out_file_combine "clef2019"