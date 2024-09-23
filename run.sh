#!/usr/bin/env bash

: "${SINCE_MINUTES_AGO:=10}";
: "${HOST_IP:=0.0.0.0}";

export TZ='Europe/Berlin';

DATE=$(date +%F)

export HOST_IP=`curl --silent --show-error ifconfig.co`
echo "HOST_IP: $HOST_IP"

docker compose build ip2geo

for f in ./log_parsers/*.sh; do bash "$f"; done | docker compose run --quiet-pull --no-TTY --env HOST_IP="${HOST_IP}" ip2geo | tee /var/storage/services/www/home/tmp/where-are-the-scanners/$DATE.json

mv /var/storage/services/www/home/tmp/where-are-the-scanners/$DATE.json /var/storage/services/www/home/tmp/where-are-the-scanners/data.json
