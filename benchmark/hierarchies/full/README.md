This directory contains 2 scripts, which generate full ICD hierarchies with their descriptiond. They require the following modules and libraries:
-re
-json
-requests
-pandas as pd
-networkx as nx
-pickle
-os
-urllib
-from collections  defaultdict
-from bs4  BeautifulSoup
-copy
-untangle

#icd-10-sp.py
-Generates 3 hierarchies: oncology (CEI-O 3.1), diagnosis (2018) and procedures (2018).
-Outputs (1 json and 1 picke file per hierarchy) are saved in "data/hierarchical_data/sp/".
	--oncology:
		-CIE 3.1 version
		-2 descriptions: full and short description
		-Levels: root, chapters ("801-804"), sections ("8010", not official, thus no description (full: no hay descripción, short: ND)), level 1 ("8010/0"), level 2 ("8010/21").
	--diagnosis:
		-2018 version
		-Levels: root, chapters ("Cap.01"), sections ("A00-A09"), level 1 ("A00"), level 2 ("A00.0"), level 3 ("A02.22").
	--procedures:
		-2018 version
		-Levels: root, chapters ("0"), sections ("001-00X"), level 1 ("00"), level 2 ("001"), level 3 ("0016"), level 4 ("00160"), level 5 ("001607"), level 6 ("0016070").
		-From level 2 to level 5 there are no descriptions ("no hay descripción" was used). The source file is completely flat, so extracting superior levels was artificially done and only descriptions that had a practical pattern were coded in the script. Information ws extracted from the corresponding manual. 

#icd-10-gm.py
-Generates ICD-10 German hierarchy for the 2016 version, but it's set up to generate the posterior versions. Simply changing the url (variable self.url) will suffice.
-Outputs (1 json and 1 picke file) are saved in "data/hierarchical_data/de/".
-Unsolved encoding issues appeared from level 2 downwards. 
-Structure of the hierarchy (from upper level to lower level):
	--root
	--chapters: "I"
	--sections: "A00-A09"
	--level 1: "A00"
	--level 2: "A00.0"
	--level 3: "A04.70"

