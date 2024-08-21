#!/usr/bin/env bash

export SINCE_MINUTES_AGO=1440
DATE=$(date +%F)

for f in ./log_parsers/*.sh; do bash "$f"; done | docker compose run --quite --no-tty ip2geo | tee /var/storage/services/www/home/tmp/where-are-the-scanners/$DATE.json

mv /var/storage/services/www/home/tmp/where-are-the-scanners/$DATE.json /var/storage/services/www/home/tmp/where-are-the-scanners/data.json
