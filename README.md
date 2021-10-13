# Codes Classification Datasets

This repository hosts scripts for publicly available datasets for the task of automatic clinical codes classification. Currently, it supports `clefnts`, `codiesp` and `cantemist`.

### Requirements

See``requirements.txt``

### Download and Process Data

```bash
DATASET=codiesp
sh $DATASET/download.sh # downloads the dataset

# (recommended) process into standard format (here we follow CLEF eHealth 2019: Task 1 format)
# output : $DATASET/data
sh $DATASET/preprocess1.sh

# (optional) process data into .JSON format (with some additional plots)
# output : $DATASET/preprocessed
sh $DATASET/preprocess2.sh
```

#### Download and Process Hierarchy

TODO