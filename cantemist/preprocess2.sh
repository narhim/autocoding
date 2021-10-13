# the following scripts pre-process from cantemist_clef formatted version
# coding, ner, norm refer to the Cantemist tracks; see README files for more info
for TRACK in coding ner norm
do
  python run_preprocess.py --data_dir cantemist --output_dir cantemist/preprocessed --partition test --track $TRACK --lang esp
  python run_preprocess.py --data_dir cantemist --output_dir cantemist/preprocessed --partition development --track $TRACK --lang esp
  python run_preprocess.py --data_dir cantemist --output_dir cantemist/preprocessed --partition training --track $TRACK --lang esp
done
