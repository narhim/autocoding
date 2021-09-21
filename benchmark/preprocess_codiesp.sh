# only run the first command once!! For repeated runs, comment out the first line to avoid duplicate data!!!
python run_preprocess.py --data_dir codiesp --subdir final_dataset_v4_to_publish --partition all --lang esp

# the following scripts pre-process from codiesp_clef formatted version
# D P X refers to the CodiEsp track; see README files for more info
# esp en are language options
for LANG in esp en
do
  for TRACK in D P X
  do
    python run_preprocess.py --data_dir codiesp --partition test --track $TRACK --lang $LANG
    python run_preprocess.py --data_dir codiesp --partition development --track $TRACK --lang $LANG
    python run_preprocess.py --data_dir codiesp --partition training --track $TRACK --lang $LANG
  done
done
