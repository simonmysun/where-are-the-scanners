import os
import sys
import geoip2.database
from json import dumps

mmdb_city_path = os.environ.get('MMMDB_CITY_PATH')
mmdb_asn_path = os.environ.get('MMMDB_ASN_PATH')

def sanitize_ip(ip):
  if '.' in ip:
    ip = ip.split('.')
    ip[-1] = 'xxx'
    ip = '.'.join(ip)
  else:
    components = ip.split(':')
    if len(components) < 8:
      expanded_address = ip.replace('::', ':' + ':'.join(['0'] * (8 - len(components) + 1 )) + ':')
      components = expanded_address.split(':')
    components[-1] = 'xxxx'
    covered_address = ':'.join([comp.lstrip('0') or '0' for comp in components])
    ip = covered_address
  return ip

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
    mmdb_source_city_response = None
    try:
      mmdb_source_city_response = mmdb_city.city(source_ip)
    except Exception as e:
      mmdb_source_city_response = 'Unknown'
      continue
    mmdb_source_asn_response = None
    try:
      mmdb_source_asn_response = mmdb_asn.asn(source_ip)
    except Exception as e:
      mmdb_source_asn_response = 'Unknown'
    mmdb_target_city_response = None
    try:
      mmdb_target_city_response = mmdb_city.city(target_ip)
    except Exception as e:
      mmdb_target_city_response = 'Unknown'
    mmdb_target_asn_response = None
    try:
      mmdb_target_asn_response = mmdb_asn.asn(target_ip)
    except Exception as e:
      mmdb_target_asn_response = 'Unknown'
    source_ip = sanitize_ip(source_ip)
    target_ip = sanitize_ip(target_ip)
    if (source_ip, target_ip, protocol) not in scanners:
      scanners[(source_ip, protocol)] = {
        "count": 1,
        "source_ip": source_ip,
        "target_ip": target_ip,
        "protocol": protocol.replace('"', '\\"'),
        "continent": mmdb_source_city_response.continent.name.replace('"', '\\"') if mmdb_source_city_response != 'Unknown' else "Unknown",
        "country": mmdb_source_city_response.country.name.replace('"', '\\"') if mmdb_source_city_response != 'Unknown' else "Unknown",
        "city": mmdb_source_city_response.city.name.replace('"', '\\"') if mmdb_source_city_response != 'Unknown' else "Unknown",
        "latitude": mmdb_source_city_response.location.latitude if mmdb_source_city_response != 'Unknown' else "Unknown",
        "longitude": mmdb_source_city_response.location.longitude if mmdb_source_city_response != 'Unknown' else "Unknown",
        "asn": mmdb_source_asn_response.autonomous_system_organization.replace('"', '\\"') if mmdb_source_asn_response != 'Unknown' else "Unknown",
        "target_latitude": mmdb_target_city_response.location.latitude if mmdb_target_city_response != 'Unknown' else "Unknown",
        "target_longitude": mmdb_target_city_response.location.longitude if mmdb_target_city_response != 'Unknown' else "Unknown"
      }
    else:
      scanners[(source_ip, protocol)]["count"] += 1
json = ''
json += '{"type": "FeatureCollection","features": ['
for scanner in scanners.values():
  json += dumps({
    "type": "Feature",
    "properties": {
      "count": scanner["count"],
      "source_ip": scanner["source_ip"],
      "target_ip": scanner["target_ip"],
      "protocol": scanner["protocol"],
      "continent": scanner["continent"],
      "country": scanner["country"],
      "city": scanner["city"],
      "asn": scanner["asn"]
    },
    "source_geometry": {
      "type": "Point",
      "coordinates": [
        scanner["longitude"],
        scanner["latitude"]
      ]
    },
    "target_geometry": {
      "type": "Point",
      "coordinates": [
        scanner["target_longitude"],
        scanner["target_latitude"]
      ]
    }
  }) + ','
json = json[:-1]
json += ']}'
print(json)
# cat *.csv | docker compose exec -T where-are-the-scanners python main.py