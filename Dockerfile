FROM python:3.9-slim AS base

RUN mkdir /challenge && chmod 700 /challenge
WORKDIR /challenge

COPY . /challenge/
RUN pip install --no-cache-dir -r requirements.txt
RUN tar czvf /challenge/artifacts.tar.gz brute_force_script.py

RUN echo "{\"flag\":\"$(cat flag.txt)\"}" > /challenge/metadata.json

EXPOSE 8087
# PUBLISH 8087 AS web

CMD ["python3", "/challenge/app.py", "--treatment", "false"]
