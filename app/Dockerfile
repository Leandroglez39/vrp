FROM python:3.8-slim
WORKDIR /app
ADD . /app
RUN apt-get update && apt-get install python3-psycopg2 -y
RUN pip install -r requirements.txt
CMD ["python","app.py"]