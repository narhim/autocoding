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
