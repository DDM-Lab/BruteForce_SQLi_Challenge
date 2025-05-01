FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG SEED
ENV SEED=${SEED}
ARG FLAG
ENV FLAG=${FLAG}

RUN mkdir /challenge && chmod 700 /challenge
RUN python setup_challenge.py

EXPOSE 8080
# The comment below is parsed by cmgr. You can reference the port by the name
# given, but if there is only one port published, you don't have to use the name
# PUBLISH 8080 AS web

CMD ["python", "app.py"]
