FROM python:3.10-alpine

WORKDIR /app

ADD * .

RUN 'python -m pip install -r requirements.txt'

ENTRYPOINT ["python", "main.py"]