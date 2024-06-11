FROM python:alpine3.20

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install -q -r requirements.txt

COPY ./ip2geo.py /app/ip2geo.py

CMD ["python", "ip2geo.py"]