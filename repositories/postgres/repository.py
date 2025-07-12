from psycopg2._psycopg import connection
from typing import List, Sequence, Any

class Repository():
    def __init__(self, db: connection):
        self.driver = db
    def insert_weather_data(self, 
                            new_data: List[Sequence[Any]]):
        cursor = self.driver.cursor()
        insert_query = """
        INSERT INTO weathers (time, temperature_2m_mean, apparent_temperature_mean, rain_sum, wind_gusts_10m_mean, wind_speed_10m_mean, relative_humidity_2m_mean)
        VALUES
        (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (time)
        DO UPDATE SET 
            temperature_2m_mean = EXCLUDED.temperature_2m_mean, 
            apparent_temperature_mean = EXCLUDED.apparent_temperature_mean, 
            rain_sum = EXCLUDED.rain_sum, 
            wind_gusts_10m_mean = EXCLUDED.wind_gusts_10m_mean, 
            wind_speed_10m_mean = EXCLUDED.wind_speed_10m_mean, 
            relative_humidity_2m_mean = EXCLUDED.relative_humidity_2m_mean;
        """
        cursor.executemany(insert_query, new_data)
        self.driver.commit()

def create_new_repository(db: connection) -> Repository:
    return Repository(db)