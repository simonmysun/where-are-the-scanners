
#!/usr/bin/env bash

: "${SINCE_MINUTES_AGO:=10}";
: "${HOST_IP:=0.0.0.0}";
LOG_PATH='/var/log/services/reverse-proxy/traefik/*';
export TZ='UTC';

DATE_SINCE=$(date --date "-${SINCE_MINUTES_AGO} min" '+%Y-%m-%dT%T');
while read -r line; do
  timestamp=$(echo "$line" | jq -r '.StartUTC');
  if [[ "$timestamp" < "$DATE_SINCE" ]]; then
    continue;
  fi
  if (($(echo "$line" | jq -r '.DownstreamStatus') < 400)); then
    continue;
  fi
  source_ip=$(echo "$line" | jq -r '.ClientHost');
  service=traefik;
  epoch_time=$(date -d "$timestamp" +%s);
  echo "$epoch_time,$HOST_IP,$source_ip,$service";
done <<< $(cat $LOG_PATH);