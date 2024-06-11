#!/usr/bin/env bash

SINCE_MINUTES_AGO="${SINCE_MINUTES_AGO:-10}";
LOG_PATH='/var/log/services/reverse-proxy/nginx/*';
export TZ='Europe/Berlin';

DATE_SINCE=$(date --date "-${SINCE_MINUTES_AGO} min" '+%d/%b/%Y:%T');
while read -r line; do
  timestamp=$(echo "$line" | awk '{print $4}' | tr -d '[' | tr -d ']' | awk -F'[: /]' '{print $2 " " $1 " " $3 " " $4 ":" $5 ":" $6 " " $7}');
  host='0.0.0.0';
  source_ip=$(echo "$line" | awk '{print $NF}' | tr -d '"');
  service=nginx;
  TZ='UTC' epoch_time=$(date -d "$timestamp" +%s);
  echo "$epoch_time,$host,$source_ip,$service";
done <<< $(cat $LOG_PATH | grep "] 404 \"" | awk -v d1=$DATE_SINCE '{gsub(/^[\[\t]+/, "", $4);}; $4 > d1');
