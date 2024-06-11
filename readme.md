# where-are-the-scanners

This tool visualizes the location of the scanners. 

![Screenshot](https://raw.githubusercontent.com/simonmysun/where-are-the-scanners/master/visualization/screenshots.png)

## See it in action

https://makelove.expert/tmp/where-are-the-scanners/?protocol=ssh%2Cnginx

## Usage

### Getting IP addresses of scanners

- Change log paths in `./log_parsers/*.sh` and execute
- `for f in ./log_parsers/*.sh; do bash "$f"; done | tee ip.csv` for the convenience
- Optionally, set `SINCE_MINUTES_AGO` to specify the time range of logs to parse, e.g. `for f in ./log_parsers/*.sh; do SINCE_MINUTES_AGO=1440 bash "$f"; done | tee ip.csv`. The default is 10 minutes.

Currently supported log parsers:

- sshd
- nginx
- traefik v2 (with JSON format)

You may also get the IP addresses of scanners from other sources. The format should be `<epoch_timestamp>,<target_ip>,<source_ip>,<protocol_or_service_name>`.

### Getting the location of the IP addresses

First you need IP databases. You can download them from https://db-ip.com/db/download/ip-to-city-lite and https://db-ip.com/db/download/ip-to-asn-lite for free (licensing terms applies). 

```bash
pip install -r requirements.txt
export MMMDB_CITY_PATH=/path/to/dbip-city.mmdb
export MMMDB_ASN_PATH=/path/to/dbip-asn.mmdb
python3 ./ip2geo.py < ip.csv > data.json
```

Alternatively, you can use docker to run the script

```bash
docker build -t ip2geo .
docker run --rm -t ip2geo < ip.csv > data.json
```

Or use docker-compose

```bash
docker compose build .
docker compose run -T ip2geo < ip.csv > data.json
```

Edit MMDB paths and volume binds in `docker-compose.yml` if necessary.

### Visualize the location of the scanners

- put `data.json` into `./visualization/` directory
- host the directory with a web server, e.g. `python3 -m http.server 8000`
- open the web page in your browser
- use query parameters to filter the data, e.g. https://makelove.expert/tmp/where-are-the-scanners/?protocol=ssh or https://makelove.expert/tmp/where-are-the-scanners/?protocol=ssh,traefik
- optionally you can specify the path to the data file with `data` query parameter, e.g. https://makelove.expert/tmp/where-are-the-scanners/?protocol=ssh,nginx&data=data.large.json

## License

Unless otherwise specified, all files in this repository are licensed under the MIT license. See the LICENSE file for more information.

- `./visualization/index.html` along with related libraries are modified from https://gist.github.com/tlfrd/df1f1f705c7940a6a7c0dca47041fec8 which is licensed with MIT.
- `./visualization/land-110m.json` is from https://github.com/topojson/world-atlas
