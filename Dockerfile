FROM python:3.9-slim AS base

RUN mkdir /challenge && chmod 700 /challenge
WORKDIR /challenge

COPY . /challenge/
RUN pip install --no-cache-dir -r requirements.txt


RUN echo "{\"flag\":\"$(cat flag.txt)\"}" > /challenge/metadata.json

RUN tar czvf /challenge/artifacts.tar.gz flag.txt

EXPOSE 8087
# The comment below is parsed by cmgr. You can reference the port by the name
# given, but if there is only one port published, you don't have to use the name
# PUBLISH 8087 AS web

CMD ["python3", "/challenge/app.py", "--treatment", "true"]

