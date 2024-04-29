FROM python:3.8-slim
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
WORKDIR /usr/src/app
COPY . .

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install --no-cache-dir -r requirements.txt

CMD exec gunicorn --bind :8085 --timeout 0 main:app
