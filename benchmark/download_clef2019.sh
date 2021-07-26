mkdir clef2019

mkdir clef2019/train_dev
wget -P clef2019/train_dev https://www.openagrar.de/servlets/MCRFileNodeServlet/openagrar_derivate_00019621/nts-icd.zip

mkdir clef2019/test
wget -P clef2019/test https://www.openagrar.de/servlets/MCRFileNodeServlet/openagrar_derivate_00021578/nts_icd.zip

cd clef2019/train_dev
unzip nts-icd.zip
cd ../test
unzip nts_icd.zip
unzip nts_icd.zip # the first command does not inflate, second time it does
cd ../..
