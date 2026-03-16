
from dotenv import load_dotenv
import os
import requests
import rocketpy
import datetime
import numpy as np

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
    envi = rocketpy.Environment(latitude=43.2557, longitude=-79.8711, elevation=250)
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)

    envi.set_date(
        (tomorrow.year, tomorrow.month, tomorrow.day, 12)
    )  # Hour given in UTC time
    envi.set_atmospheric_model(type="Forecast", file="GFS")

    return envi

def get_base_forecast():
    """Downloads GFS data ONCE. This is the slow part."""
    # As per RocketPy docs: date (and optionally lat/lon, max_expected_height) in Environment()
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    launch_date = (tomorrow.year, tomorrow.month, tomorrow.day, 12)
    print(":-----------------1")
    envi = rocketpy.Environment(
        latitude=48.4758,
        longitude=-81.3305,
        elevation=110,
        date=(tomorrow.year, tomorrow.month, tomorrow.day, 12),
        max_expected_height=9100,
    )
    print("Downloading GFS Forecast Data (this may take a moment)...")
    envi.set_atmospheric_model(type="Forecast", file="GFS")
    return envi

def use_chosen_day(envi):
    # 1. Locate the file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "transformedWindData/transformed_20231126_1800_006.csv")

    # 2. Load your custom data 
    data = np.loadtxt(file_path, delimiter=",", skiprows=0)
    h, u, v = data[:, 0], data[:, 1], data[:, 2]
    print(h,u,v)

    # 3. Setup dates
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    launch_date = (tomorrow.year, tomorrow.month, tomorrow.day, 12)
   
    # 5. Initialize 'env' as a copy/new instance to overwrite
    env = rocketpy.Environment(
        latitude=48.4758,
        longitude=-81.3305,
        elevation=110,
        max_expected_height=9100,
    )
    print(np.column_stack((h, u)))
    print(np.column_stack((h, v)))
    # 6. Apply Custom Wind to 'env' while pulling Temp/Pressure from 'envi'
    env.set_atmospheric_model(
        type="custom_atmosphere",
        wind_u=np.column_stack((h, u)),
        wind_v=np.column_stack((h, v)),
        temperature=envi.temperature, # Tracing from 'envi'
        pressure=envi.pressure        # Tracing from 'envi'

    )

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