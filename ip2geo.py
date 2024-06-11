import os
import sys
import geoip2.database

mmdb_city_path = os.environ.get('MMMDB_CITY_PATH')
mmdb_asn_path = os.environ.get('MMMDB_ASN_PATH')

scanners = dict()

with geoip2.database.Reader(mmdb_city_path) as mmdb_city, geoip2.database.Reader(mmdb_asn_path) as mmdb_asn:
  for line in sys.stdin:
    line = line.strip()
    if not line:
      continue
    line = line.split(',')
    timestamp = line[0]
    target_ip = line[1]
    source_ip = line[2]
    protocol = line[3]
    mmdb_city_response = None
    try:
      mmdb_city_response = mmdb_city.city(source_ip)
    except Exception as e:
      mmdb_city_response = 'Unknown'
      continue
    mmdb_asn_response = None
    try:
      mmdb_asn_response = mmdb_asn.asn(source_ip)
    except Exception as e:
      mmdb_asn_response = 'Unknown'
    if (source_ip, protocol) not in scanners:
      scanners[(source_ip, protocol)] = {
        "count": 1,
        "source_ip": source_ip,
        "protocol": protocol.replace('"', '\\"'),
        "continent": mmdb_city_response.continent.name.replace('"', '\\"') if mmdb_city_response != 'Unknown' else "Unknown",
        "country": mmdb_city_response.country.name.replace('"', '\\"') if mmdb_city_response != 'Unknown' else "Unknown",
        "city": mmdb_city_response.city.name.replace('"', '\\"') if mmdb_city_response != 'Unknown' else "Unknown",
        "latitude": mmdb_city_response.location.latitude if mmdb_city_response != 'Unknown' else "Unknown",
        "longitude": mmdb_city_response.location.longitude if mmdb_city_response != 'Unknown' else "Unknown",
        "asn": mmdb_asn_response.autonomous_system_organization.replace('"', '\\"') if mmdb_asn_response != 'Unknown' else "Unknown"
      }
    else:
      scanners[(source_ip, protocol)]["count"] += 1
json = ''
json += '{"type": "FeatureCollection","features": ['
for scanner in scanners.values():
  json += '{"type": "Feature","properties": {'
  json += f'"count": {scanner["count"]},'
  json += f'"source_ip": "{scanner["source_ip"]}",'
  json += f'"protocol": "{scanner["protocol"]}",'
  json += f'"continent": "{scanner["continent"]}",'
  json += f'"country": "{scanner["country"]}",'
  json += f'"city": "{scanner["city"]}",'
  json += f'"asn": "{scanner["asn"]}"'
  json += '},"geometry": {"type": "Point","coordinates": ['
  json += f'{scanner["longitude"]},'
  json += f'{scanner["latitude"]}'
  json += ']}},'
json = json[:-1]
json += ']}'
print(json)
# cat *.csv | docker compose exec -T where-are-the-scanners python main.py