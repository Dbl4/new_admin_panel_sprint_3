FROM python:3.10-slim-buster

WORKDIR /postgres_to_es

COPY requirements.txt ./
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

EXPOSE 9200/tcp

RUN python load_data.py