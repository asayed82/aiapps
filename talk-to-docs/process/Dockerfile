FROM python:3.11


ENV PYTHONUNBUFFERED True

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir  -r requirements.txt

ENTRYPOINT ["python", "process.py"]