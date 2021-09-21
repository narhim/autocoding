# Automatic Codes Classification

## Preprocessing

### Requirements

- python 3.7+
- matplotlib==3.4.x (lower version will result in errors during plotting)
- seaborn (for plotting)
- skmultilearn (for iterative stratified splitting; necessary for guttman preprocessing)

See``requirements.txt``

### clef2019
- Running the preprocessing script will generate the following files in ``preprocessed/clef2019`` 
    - test/training/development.json
    - unseen label files; each line contains an unseen label as described in file names 
      (if file is empty -> no unseen labels)
    - label distribution for each partition

### guttman

- Prior to running the pre-processing script, re-save the ``annotaion_Conny_final.xlsm``
file to be **non-password-protected** locally.  (e.g. ``annotation_Conny_final_npwd.xlsm`` is the default filename in the
  script)
- The pre-processing script assumes both the ``annotation_Conny_final_npwd.xlsm`` and ``output.txt`` files are
in the same directory (benchmark/guttman/<both files should be in here>)
- Running ``preprocess_guttman.sh`` will generate:
    - the first line of the script generates the raw data files as described below, **uncomment the first line for repeated runs to avoid having duplicate files**
    - The raw data files are in the same organization as ``clef2019`` dataset, which can be pre-processed with the same
      steps for preprocessing ``clef2019``
    - <train/dev/test>.json files inside the ``preprocessed/guttman`` directory.
    - plots for each partition class label distribution in ``preprocessed/guttman/plots``
    - unseen label files as described in ``clef2019`` preprocessing
- random seed: 38 (the script tested 10 seeds from 35 to 45; no need to specify)
- **output .json files >> train: 501 (0.60), dev: 246 (0.30), test: 87 (0.10), total 834 samples.**
- partitions are made to preserve the class labels distribution in the whole dataset

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
  

### cantemist

TBD            
            