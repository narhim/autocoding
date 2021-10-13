This directory contains 3 scripts that generate hierarchies and saved them in json and pickle files. They are all run from the bash scripts in the parent directory and require the following:

-The correspondent dataset to be already downloaded. Paths are defined in each script, thus might require adjustment.
-The correspondent full-extent ICD hierarchy to be generated (they are previously generated in the bash script). Each script generates the hierarchy based on the full-extent hierarchy and the correspondent codes for ech subset.
-The following modules and libraries:
	--os
	--pickle
	--json
	--networkx

#clef2019_parser.py


#cantemist_parser.py


#codiesp_parser.py