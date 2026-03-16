from rocketpy import Environment
env = Environment(latitude=32.990254, longitude=-106.974998, elevation=1400)
import datetime

tomorrow = datetime.date.today() + datetime.timedelta(days=1)

env.set_date(
    (tomorrow.year, tomorrow.month, tomorrow.day, 12)
)  # Hour given in UTC time
env.set_atmospheric_model(type="Forecast", file="GFS")
env.info()