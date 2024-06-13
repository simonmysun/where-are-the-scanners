#!/usr/bin/env bash

SINCE_MINUTES_AGO="${SINCE_MINUTES_AGO:-10}";
LOG_PATH='/var/log/services/reverse-proxy/nginx/*';
export TZ='Europe/Berlin';

host=`uname -n`;

DATE_SINCE=$(date --date "-${SINCE_MINUTES_AGO} min" '+%s');
cat $LOG_PATH | grep -v '\[error\]' | {
  while read -r line; do
    status=$(echo "$line" | awk '{print $6}');
    if (( status < 400 )); then
      continue;
    fi
    timestamp=$(echo "$line" | awk '{print $4 " " $5}' | tr -d '[' | tr -d ']' | awk -F'[: /]' '{print $2 " " $1 " " $3 " " $4 ":" $5 ":" $6 " " $7}') 
    epoch_time=$(date -d "$timestamp" +%s);
    if (( epoch_time < DATE_SINCE )); then
      continue;
    fi
    source_ip=$(echo "$line" | awk '{print $NF}' | tr -d '"');
    service=nginx;
    echo "$epoch_time,$host,$source_ip,$service";
  done
};
