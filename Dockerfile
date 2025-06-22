FROM python:3.12-slim

WORKDIR /app

COPY . ./

RUN apt-get update && apt-get -y install cron && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt

RUN echo "0 0 * * * cd /app && python fetch_weather_data.py >> /var/log/cron.log 2>&1" > /etc/cron.d/fetch-weather-job

RUN chmod 0644 /etc/cron.d/fetch-weather-job

RUN crontab /etc/cron.d/fetch-weather-job

RUN touch /var/log/cron.log

RUN echo "script started"

# Start cron and keep container running
CMD ["/bin/sh", "-c", "cron && tail -f /var/log/cron.log"]