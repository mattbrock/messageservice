#!/bin/bash

# Dynamically generates inventory output for specific environment, for Ansible to use for deployments.

if [ "$1" == "--list" ] ; then

  instances=$(aws ec2 describe-instances --filters "Name=tag:Service,Values=MessageService" "Name=instance-state-name,Values=running" --query "Reservations[].Instances[].PublicDnsName" --output text --region eu-west-2)
  no_instances=$(echo $instances | wc -w)

  i=1
  echo -en "{\n  \"messageservice\": {\n    \"hosts\": ["
  for instance in $instances ; do
    if [ $i -lt $no_instances ] ; then
      echo -en "\"$instance\", "
    else
      echo -en "\"$instance\""
    fi
    ((i=$i+1))
  done
  echo -en "],\n    \"vars\": {}\n  }\n}\n"

elif [ "$1" == "--host" ] ; then

  echo -en "{\n  \"_meta\": {\n    \"hostvars\": {}\n  }\n}\n"

fi
