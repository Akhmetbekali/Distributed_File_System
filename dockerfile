FROM python:3.7.4

WORKDIR .

ADD . .

RUN pip3 install -r requirements.txt

CMD python3 storage.py