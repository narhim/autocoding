python run_preprocess.py --data_dir guttman --partition all # comment out this line if repeating repeating runs to avoid generating duplicate data files
python run_preprocess.py --data_dir guttman --partition test
python run_preprocess.py --data_dir guttman --partition development
python run_preprocess.py --data_dir guttman --partition training