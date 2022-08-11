# bin/bash
BOOTSTRAP_VERSION=5.1.3
BOOTSTRAP=bootstrap-${BOOTSTRAP_VERSION}-examples
mkdir ./html
rm -rf ${BOOTSTRAP} && rm -rf ./html/assets
wget https://github.com/twbs/bootstrap/releases/download/v${BOOTSTRAP_VERSION}/${BOOTSTRAP}.zip && unzip ${BOOTSTRAP}.zip && rm -rf ${BOOTSTRAP}.zip
mv ./${BOOTSTRAP}/assets ./html/assets && rm -rf ${BOOTSTRAP}
./dl_fundament.sh