This directory contains 4 scripts, one (common.py) with common functions to all other scripts, and the other 3 generate hierarchies and save them in json and pickle files. They are all run from the bash scripts in the parent directory and require the following:

-The correspondent dataset to be already downloaded. Paths are defined in each script, thus might require adjustment.
-The correspondent full-extent ICD hierarchy to be generated (they are previously generated in the bash script). Each script generates the hierarchy based on the full-extent hierarchy and the correspondent codes for ech subset.
-The following modules and libraries:
	--os
	--pickle
	--json
	--networkx
	--argparse

#clef2019_parser.py
-The German edition for CLEF2019 has two partitions: train_dev and test, thus 2 hierarchies and 4 files (1 json, 1pickle per hierarchy) are generated. 
-Its codes are the ICD-10 German edition from 2016. Since it only includes sections, they hierarchy doesn't go any further.
-Outputs are saved in the directory "data/hierarchical_data/de/clef2019/"

#cantemist_parser.py
-CANTEMIST has two tasks with codes: __norm__ and __coding__, and 4 partitions: train, dev1, dev2, and test. One hierarchy (saved in one json and in one pickle file) is generated for each combination.
-Its codes are from the Spanish version of ICD-O (CIE-O 3.1 in Spanish).
-Several codes from CANTEMIST are not in the official hierarchy. All have been added following their pattern, but it was not always possible to add a description. In such cases the full description "no hay descripción" (there is no description, short description ND), was used. Otherwise descriptions were generted using the patterns in the CIE-O 3.1 manual.
-Outputs are saved in the directory "data/hierarchical_data/sp/cantemist/"

#codiesp_parser.py
-CODIESP 2020 has three tasks: diagnosis, procedures and x (mixture of both); and 3 partitions: train, dev, test.
-Its codes are from the Spanish 2018 version of ICD-10 codes (CIE-10 in Spanish).
-Running the full script takes considerably long (more than 20 minutes).
-Outputs are saved in the directory "data/hierarchical_data/sp/codiesp/"