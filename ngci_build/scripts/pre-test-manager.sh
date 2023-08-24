#!/bin/bash
set -e


pwd
cp .cicd/manager_secrets.json /tmp/manager_secrets
sed -i \
 -e "s/MYSQL_DATABASE/${MYSQL_DATABASE}/g" \
 -e "s/MYSQL_ROOT_PASSWORD/${DB_PASSWORD}/g" \
 -e 's#"SERVER": "mysql"#"SERVER": "127.0.0.1"#g' \
  /tmp/manager_secrets


cat /tmp/manager_secrets

