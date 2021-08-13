# Automatic Codes Classification

## Preprocessing

### Requirements

- python 3.7+
- matplotlib==3.4.x (lower version will result in errors during plotting)
- seaborn (for plotting)
- skmultilearn (for iterative stratified splitting; necessary for guttman preprocessing)

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
    - the first line of the script generates the raw data files as described below, uncomment the first line for subsequent runs to avoid having duplicate files
    - Data files in the same organization as ``clef2019`` dataset, which can be pre-processed with the same
      steps for preprocessing ``clef2019``
    - a <train/dev/test>.json inside the ``preprocessed/guttman`` directory.
    - plots for each partition class label distribution in ``preprocessed/guttman/plots``
- best random seed: 38 (the script tested 10 seeds from 35 to 45; no need to specify)
- train: 501 (0.60), dev: 246 (0.30), test: 87 (0.10), total 834 samples.
- partitions are made to preserve the class labels distribution in the whole dataset
