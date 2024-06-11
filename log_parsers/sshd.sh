#!/usr/bin/env bash

SINCE_MINUTES_AGO="${SINCE_MINUTES_AGO:-10}";
export TZ='Europe/Berlin';

while read -r line; do
  timestamp=$(echo "$line" | awk '{print $1" "$2" "$3}');
  host=$(echo "$line" | awk '{print $4}');
  source_ip=$(echo "$line" | awk -F'rhost=' '{print $2}' | awk '{print $1}');
  service=ssh;
  if [ -z "$source_ip" ]; then
    source_ip=$(echo "$line" | awk '{print $13}');
  fi
   TZ='UTC' epoch_time=$(date -d "$timestamp" +%s);
  echo "$epoch_time,$host,$source_ip,$service";
done <<< $(journalctl -u sshd --since "${SINCE_MINUTES_AGO}min ago" | grep 'uthentication failure\|Failed password for invalid user');