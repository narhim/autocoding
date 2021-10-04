# only run the first command once!! For repeated runs, comment out the first line to avoid duplicate data!!!
python run_preprocess.py --data_dir cantemist --partition all --lang esp

# the following scripts pre-process from cantemist_clef formatted version
# coding, ner, norm refer to the Cantemist tracks; see README files for more info
for TRACK in coding ner norm
do
  python run_preprocess.py --data_dir cantemist --partition test --track $TRACK --lang esp
  python run_preprocess.py --data_dir cantemist --partition development --track $TRACK --lang esp
  python run_preprocess.py --data_dir cantemist --partition training --track $TRACK --lang esp
done