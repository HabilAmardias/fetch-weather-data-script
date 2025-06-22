import openmeteo_requests
from datetime import date, timedelta
import pandas as pd
import numpy as np
from repositories.supabase.repository import create_supabase_repository
from os import environ
from dotenv import load_dotenv
import logging

def get_data():
    client = openmeteo_requests.Client()
    url = 'https://archive-api.open-meteo.com/v1/archive'
    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=4)
    params = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'latitude': -6.428865,
        'longitude': 106.924057,
        "timezone": "Asia/Bangkok",
        'daily': ["temperature_2m_max", 
                  "temperature_2m_min", 
                  "apparent_temperature_max", 
                  "apparent_temperature_min", 
                  "daylight_duration", 
                  "sunshine_duration", 
                  "wind_speed_10m_max", 
                  "wind_gusts_10m_max"]
    }
    response = client.weather_api(url, params=params)[0]

    daily = response.Daily()
    daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
    daily_apparent_temperature_max = daily.Variables(2).ValuesAsNumpy()
    daily_apparent_temperature_min = daily.Variables(3).ValuesAsNumpy()
    daily_daylight_duration = daily.Variables(4).ValuesAsNumpy()
    daily_sunshine_duration = daily.Variables(5).ValuesAsNumpy()
    daily_wind_speed_10m_max = daily.Variables(6).ValuesAsNumpy()
    daily_wind_gusts_10m_max = daily.Variables(7).ValuesAsNumpy()

    daily_data = {"time": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}

    daily_data["temperature_2m_max (°C)"] = daily_temperature_2m_max
    daily_data["temperature_2m_min (°C)"] = daily_temperature_2m_min
    daily_data["apparent_temperature_max (°C)"] = daily_apparent_temperature_max
    daily_data["apparent_temperature_min (°C)"] = daily_apparent_temperature_min
    daily_data["daylight_duration (s)"] = daily_daylight_duration
    daily_data["sunshine_duration (s)"] = daily_sunshine_duration
    daily_data["wind_speed_10m_max (km/h)"] = daily_wind_speed_10m_max
    daily_data["wind_gusts_10m_max (km/h)"] = daily_wind_gusts_10m_max

    daily_data = pd.DataFrame(data = daily_data)

    return daily_data

def transform_data(df:pd.DataFrame):
    df['time'] = pd.to_datetime(df['time'])
    df.sort_values('time',inplace=True)

    if df.isna().sum().values.sum().item() > 0:
        df = df.replace({pd.NA: None, float('nan'): None, np.nan: None})

    df['time'] = df['time'].dt.strftime('%Y-%m-%d')

    return df

if __name__ == '__main__':
    load_dotenv()
    logger = logging.getLogger("Weather Fetcher")
    logging.basicConfig(level=logging.INFO)
    repo = create_supabase_repository()

    data = get_data()
    transformed = transform_data(data)

    try:
        repo.insert_data(transformed, environ.get("WEATHER_BUCKET"))
        logger.info("Success Insert Data")
    except Exception as e:
        logger.error(repr(e))