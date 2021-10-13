### codiesp

- Running the ``preprocess_codiesp.sh`` script will first re-format the dataset to clef2019 format. This will be saved in a
separate directory (``codiesp_clef`` is the default directory name)
- **!!WARNING!! Comment out the first line of command AFTER the first run to prevent duplicate entries in ``codiesp_clef``**
- The re-formatted files are then be pre-processed and analyzed with the same pre-processing steps as the clef2019
dataset
- the ``preprocess_codiesp.sh`` generates:
  - <train/dev/test>.json files inside the ``preprocessed/codiesp_clef`` directory
  - all 3 label versions are provided: "D" (diagnostic codes only), "P" (procedure codes only), "X" (both)
  - the text files and file IDs in the train/dev/test partitions are identical regardless of the label version
  - Both "esp" (Spanish) and "en" (English) versions are included
  - label id - label description dictionary is only available for Spanish (pending)
  - ``preprocessed/codiesp_clef`` directory structure is as follows:
      - codiesp_clef:
        - esp | en:
            - D | P | X:
                - plots:
                  - label frequency distribution plots
                - <train/dev/text>.json files
                - <a_partition>unseen_labels<another_partition>.txt
  
