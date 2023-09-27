FROM python:3.11

COPY ./requirements.txt ./server/requirements.txt

RUN pip install --upgrade pip

RUN pip install -r /server/requirements.txt

COPY ./ ./server

WORKDIR ./server
