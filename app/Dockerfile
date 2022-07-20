FROM python:3.9-slim-buster

COPY . .

EXPOSE 8220:8000

RUN pip install -r requirements.txt

CMD python flask_app.py
