
from dotenv import load_dotenv
import os
import numpy as np
import requests
import rocketpy
import datetime

load_dotenv()
api_key = os.getenv("WEATHER_API_KEY")


def get_weather(lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"
    response = requests.get(url)

    data = response.json()

    return data
        # "feels_like": data["main"]["feels_like"],
        # "pressure": data["main"]["pressure"],
        # "humidity": data["main"]["humidity"],
        # "wind_speed": data["wind"]["speed"],
        # "wind_deg": data["wind"]["deg"],
        # "description": data["weather"][0]["description"],
        # "clouds": data["clouds"]["all"],

#standard
def standard_get_weather():
    envi = rocketpy.Environment(latitude=43.2557, longitude=-79.8711, elevation=1400)
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)

    envi.set_date(
        (tomorrow.year, tomorrow.month, tomorrow.day, 12)
    )  # Hour given in UTC time
    envi.set_atmospheric_model(type="Forecast", file="GFS")
    envi.max_expected_height = 20000
    envi.info()
    return envi

def NOAA_Sucks_Weather():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    # csv_path = os.path.join(project_root, "transformedWindData", "transformed_2025081100-73111.csv")
    csv_path = os.path.join(project_root, "TestGeneration", "FastUV", "FastDay_UV.csv")

    data = np.loadtxt(csv_path, delimiter=",", skiprows=1)
    h, u, v = data[:, 0], data[:, 1], data[:, 2]
    wind_u = list(zip(h, u))
    wind_v = list(zip(h, v))

    envi = rocketpy.Environment(latitude=43.2557, longitude=-79.8711, elevation=1400)
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    envi.set_date((tomorrow.year, tomorrow.month, tomorrow.day, 12))
    envi.max_expected_height = 20000
    envi.set_atmospheric_model(
        type="custom_atmosphere",
        pressure=None,
        temperature=None,
        wind_u=wind_u,
        wind_v=wind_v,
    )
    return envi