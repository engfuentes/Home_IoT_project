FROM python:3.9-slim

WORKDIR /usr/src/app

COPY /sensor_publisher/requirements.txt .

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "BME280_sensor_client.py"]