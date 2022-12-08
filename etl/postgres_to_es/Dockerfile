FROM python:3.10-slim-buster

WORKDIR /postgres_to_es

COPY ./requirements.txt ./
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . ./

CMD python load_data.py