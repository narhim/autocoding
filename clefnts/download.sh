mkdir clefnts/data

mkdir clefnts/data/train_dev
wget -P clefnts/data/train_dev https://www.openagrar.de/servlets/MCRFileNodeServlet/openagrar_derivate_00019621/nts-icd.zip

mkdir clefnts/data/test
wget -P clefnts/data/test https://www.openagrar.de/servlets/MCRFileNodeServlet/openagrar_derivate_00021578/nts_icd.zip

cd clefnts/data/train_dev
unzip nts-icd.zip
cd ../test
unzip nts_icd.zip
unzip nts_icd.zip # the first command does not inflate, second time it does
cd ../../..
