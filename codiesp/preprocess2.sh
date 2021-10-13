# the following scripts pre-process from codiesp_clef formatted version
# D P X refers to the CodiEsp track; see README files for more info
# esp en are language options
for LANG in esp en
do
  for TRACK in D P X
  do
    python run_preprocess.py --data_dir codiesp --output_dir codiesp/preprocessed --partition test --track $TRACK --lang $LANG
    python run_preprocess.py --data_dir codiesp --output_dir codiesp/preprocessed --partition development --track $TRACK --lang $LANG
    python run_preprocess.py --data_dir codiesp --output_dir codiesp/preprocessed --partition training --track $TRACK --lang $LANG
  done
done
