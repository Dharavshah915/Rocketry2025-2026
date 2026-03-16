from rocketpy import Environment
env = Environment(latitude=32.990254, longitude=-106.974998, elevation=1400)
import datetime

tomorrow = datetime.date.today() + datetime.timedelta(days=1)

env.set_date(
    (tomorrow.year, tomorrow.month, tomorrow.day, 12)
)  # Hour given in UTC time
env.set_atmospheric_model(
    type="custom_atmosphere",
    pressure=None,     # Uses Standard Atmosphere pressure
    temperature=None,  # Uses Standard Atmosphere temperature
    wind_u=[(0, 5), (5000, 15)], # Eastward wind (height, speed)
    wind_v=[(0, 2), (5000, 5)]   # Northward wind (height, speed)
)
env.info()