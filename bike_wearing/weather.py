import requests
import urllib.parse
from datetime import datetime, timedelta


BASE_URL = "https://api.open-meteo.com/v1/forecast"
static_params = static_params = {
    "latitude": "48.5495",
    "longitude": "7.7931",
    "hourly": "temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature,wind_speed_10m,wind_direction_10m,soil_temperature_0cm",
    "timezone": "Europe/Berlin",
}


def get_weather_at_time(dtime: datetime) -> dict:
    start_hour = dtime.strftime("%Y-%m-%dT%H:%M")
    end_hour = (dtime + timedelta(minutes=20)).strftime("%Y-%m-%dT%H:%M")
    static_params.update({"start_hour": start_hour, "end_hour": end_hour})
    url_complete = BASE_URL + "?" + urllib.parse.urlencode(static_params)
    resp = requests.get(url_complete)
    if resp.status_code == 200:
        weather_data = resp.json()
        weather_data["hourly"].pop("time")
        weather_data = {k: v[0] for k, v in weather_data["hourly"].items()}
        return weather_data
    else:
        raise ValueError()


if __name__ == "__main__":
    get_weather_at_time()
