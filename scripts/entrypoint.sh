#!/bin/bash

. /kb/deployment/user-env.sh

python ./scripts/prepare_deploy_cfg.py ./deploy.cfg ./work/config.properties

if [ -f ./work/token ] ; then
  export KB_AUTH_TOKEN=$(<./work/token)
fi

if [ $# -eq 0 ] ; then
  sh ./scripts/start_server.sh
elif [ "${1}" = "test" ] ; then
  echo "Run Tests"
  make test
elif [ "${1}" = "async" ] ; then
  sh ./scripts/run_async.sh
elif [ "${1}" = "init" ] ; then
  echo "Initialize module"
  cd /data
  ORTHOLOG_FILE="Phytozome_Ortholog_Mapping.tar.gz"
  wget http://bioseed.mcs.anl.gov/~seaver/Files/${ORTHOLOG_FILE}
  tar -zxf $ORTHOLOG_FILE
  if [ -f "Phytozome_Ortholog_Mapping.json" ] ; then
      touch __READY__
      echo "Init succeeded"
  else
      echo "Init failed"
  fi
elif [ "${1}" = "bash" ] ; then
  bash
elif [ "${1}" = "report" ] ; then
  export KB_SDK_COMPILE_REPORT_FILE=./work/compile_report.json
  make compile
else
  echo Unknown
fi
