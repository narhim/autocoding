#!/bin/bash
python3 benchmark/icd-10-sp.py --url "https://eciemaps.mscbs.gob.es/ecieMaps/download?name=2018_CIEO31_TABLA_%20REFERENCIA_con_6_7_caracteres_final_20180111_5375350050755186721_7033700654037542595.xlsx" --output_dir "data/hierarchical_data/sp/" --file_name "icd-o-sp"
#Only oncology hierarchy for the moment