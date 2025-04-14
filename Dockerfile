
FROM python:3.9-slim

WORKDIR /app

ENV TREATMENT=True

COPY . /app

RUN pip install --no-cache-dir flask

EXPOSE 8087

CMD ["python", "app.py","--treatment","true"]
