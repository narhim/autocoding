### cantemist

- Running the ``preprocess_cantemist.sh`` script will first re-format the dataset to clef2019 format. This will be saved in a
  separate directory (``cantemist_clef`` is the default directory name)
- **!!WARNING!! Comment out the first line of command AFTER the first run to prevent duplicate entries in ``cantemist_clef``**
- The re-formatted files are then be pre-processed and analyzed with the same pre-processing steps as the clef2019
  dataset
- the ``preprocess_cantemist.sh`` generates:
    - <train/dev/test>.json files inside the ``preprocessed/cantemist_clef`` directory
    - all 3 label tracks are provided: "coding", "ner", "norm". See the README.txt file in the original Cantemist directory for more details
    - the text files and file IDs in the train/dev/test partitions are identical regardless of the label track
    - There's only "esp" (Spanish) langugae data available for the Cantemist dataset
    - label id - label description dictionary is pending (currently not available)
    - ``preprocessed/cantemist_clef`` directory structure is as follows:
        - cantemist_clef:
            - esp:
                - coding | ner | norm:
                    - plots:
                        - label frequency distribution plots
                    - <train/dev/text>.json files
                    - <a_partition>unseen_labels<another_partition>.txt
- Original Cantemist dataset includes **repeated labels** in a document according to the number of times the label(s) 
  appear in the document. **This is preserved in the pre-processed .json files.** i.e. list of labels for some file IDs 
  may contain duplicate labels as per the original annotation files.
- May add an option to only include unique labels / document (pending)
