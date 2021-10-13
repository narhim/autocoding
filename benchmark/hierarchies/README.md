#Hierarchies

#General 


#German
download_icd_gm_hieraarchy.sh: runs two scripts:
	icd-10-gm.py: generates a graph with the full ICD-10 German hierarchy with codes and descriptions, converts it to a dictionary and saves it into a json and a pickle file. Set up to generate the 2016 hierarchy (one used in clef2019), but, if url is changed, the 2019, 2020, and 2021 can be generated.
	clef2019_parser.py: from 

#SPANISH

All hierarchies for ICD codes in Spanish are generated with download_icd_sp_hierarchy.sh. Comments for specific hierarchies: 

#CIE-O-3.1 (ICD-O in English)

ICD codes for oncology in Spanish, 3.1 version (2018). Its hierarchy is generated with the class SpaICD_O_Hierarchy within the script icd-10-sp.py and saved both as a pickle and a json file in data/hierarchical_data/sp/ as icd-o-sp. Codes are obtained from https://eciemaps.mscbs.gob.es/ecieMaps/download?name=2018_CIEO31_TABLA_%20REFERENCIA_con_6_7_caracteres_final_20180111_5375350050755186721_7033700654037542595.xlsx . Some comments:

-The hierarchy has 4 levels: root, grandparents/chapters (e.g.:8156), parents/sections (e.g.:8156/3), and children/subsections (e.g.:8156/31). 
	-The last two are extracted directly from the url, and thus, they keep the full and short descriptions.
	-The chapters are inferred from the parents and children, and thus, don't have any kind of description.


#CANTEMIST (Spanish)

The CANTEMIST task is subdivided into three subtasks: coding, norm and ner. Of these, only the first two use codes from the ICD-O (CIE-O-3.1 in Spanish), their hierarchies are parsed with cantemist_parser.py from the CIE-O-3.1 hierarchies generated before. All files generated are saved in data/hierarchical_data/sp/cantemist. Some comments:

-Each task is subdivided into 4 subsets: train, dev1, dev2 and test. Hierarchies for each one are generated, none for any conbination of datasets. Hierarchies are saved both in json and pickle files that have the following name pattern cantemist_dataset_task.
-If a section (as defined above for full ICD-O) is in the hierarchy it means that either it is explicilty in the set or that its child(ren) is(are) in the specific set. 
-Surprisingly, in every dataset they are codes that are not specifically found in the CIE-O-3.1 hierarchy, at least not explicitly. Not being able to find the cause of this, a separate txt file with the unseen codes in each task is generated. Name follows the pattern cantemist_task_not_in_H.
-Full and short descriptions from the CIE-O-3.1 hierarchies are kept.  