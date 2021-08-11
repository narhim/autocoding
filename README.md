# Automatic Codes Classification

## Preprocessing

### Requirements

- python 3.7
- matplotlib==3.4.x
- seaborn (for plotting)
- skmultilearn (for iterative stratified splitting)

### clef2019
- Running the preprocessing script will generate the following files in ``preprocessed/clef2019`` 
    - test/training/development.json
    - unseen label files; each line contains an unseen label as described in file names 
      (if file is empty -> no unseen labels)
    - label distribution for each partition

### guttman

- Prior to running the pre-processing script, re-save the ``annotaion_Conny_final.xlsm``
file to be _non-password-protected_ locally.  
- The pre-processing script assumes both the ``annotation_Conny_final.xlsm`` and ``output.txt`` files are
in the same directory (benchmark/guttman/<both files should be in here>)
- The script will generate a <train/dev/test>.json
inside the ``preprocessed/guttman`` directory.
