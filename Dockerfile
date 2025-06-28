FROM python:3.12-slim

WORKDIR /app

COPY . ./

# Install required packages including timezone data
RUN apt-get update && apt-get -y install cron tzdata && rm -rf /var/lib/apt/lists/*

# Set timezone to GMT+7 (Asia/Jakarta)
ENV TZ=Asia/Jakarta
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt

# Create cron job for 00:00 GMT+7 (which is 17:00 UTC the previous day)
RUN echo "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" > /etc/cron.d/fetch-weather-job && \
    echo "0 0 * * * root cd /app && /usr/local/bin/python fetch_weather_data.py >> /var/log/cron.log 2>&1" >> /etc/cron.d/fetch-weather-job && \
    echo "" >> /etc/cron.d/fetch-weather-job

RUN chmod 0644 /etc/cron.d/fetch-weather-job
RUN crontab /etc/cron.d/fetch-weather-job
RUN touch /var/log/cron.log

# Start cron service and tail the log
CMD ["/bin/sh", "-c", "service cron start && tail -f /var/log/cron.log"]