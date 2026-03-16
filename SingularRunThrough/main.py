

# api_key = os.getenv("WEATHER_API_KEY")

# report = ExternalEnviornmentalFactorsSetup.get_weather(lat=43.2557, lon=-79.8711, api_key=api_key)
# print(report)

# city = report['name']                       # 'Hamilton'
# temperature = report['main']['temp']        # 5.87
# feels_like = report['main']['feels_like']   # 2.36
# pressure = report['main']['pressure']       # 1017
# humidity = report['main']['humidity']       # 65
# weather_desc = report['weather'][0]['description']  # 'broken clouds'
# wind_speed = report['wind']['speed']        # 5.14
# wind_deg = report['wind']['deg']            # 280

# print(city, temperature, feels_like, pressure, humidity, weather_desc, wind_speed, wind_deg)

print("---------------------------------------------------")

# env = rocketpy.Environment(latitude=43.2557, longitude=-79.8711, elevation=1400)
# tomorrow = datetime.date.today() + datetime.timedelta(days=1)

# env.set_date(
#     (tomorrow.year, tomorrow.month, tomorrow.day, 12)
# )  # Hour given in UTC time
# env.set_atmospheric_model(type="Forecast", file="GFS")
# env.max_expected_height = 5000
# env.info()
case = 1;

if (case ==1):
    from dotenv import load_dotenv
    import matplotlib.pyplot as plt
    import os
    import rocketpy
    import ExternalEnviornmentalFactorsSetup as Envi
    import Motor
    import Rocket
    import Aerodynamic_Surfaces as As
    import Parachute
    import datetime
    from rocketpy.utilities import fin_flutter_analysis

    plt.ion() # lets the plots appear and the code will continue to run

    print("-----Define Weather----------------------------------------------")
    envi = Envi.NOAA_Sucks_Weather()
    print("--------------Defene Solid Motor-------------------------------------")
    motor1 = Motor.define_motor()
    print("------------------Define Rocket---------------------------------")
    rocket = Rocket.define_rocket()
    print("------------------Add Motor to Rocket---------------------------------")
    rocket.add_motor(motor1, position=-1.255)
    print("------------------dine rocket fins, nose cone, and tail---------------------------------")
    As.define_surfaces(rocket)
    print("------------------Add Parachutes---------------------------------")
    Main, Drouge = Parachute.add_parachutes(rocket, 0.5)
    print("------------------Flight Sim---------------------------------")
    test_flight = rocketpy.Flight(
        rocket=rocket, environment=envi, rail_length=3.6576, inclination=90-4, heading=70
    )


    flutter_results = fin_flutter_analysis(
        flight=test_flight,
        fin_thickness=0.007366,  
        shear_modulus=4.702e9,
        see_prints=True,
        see_graphs=False,   
    )
    plt.show()

    test_flight.plots.trajectory_3d()
    plt.savefig("trajectory.png")

    print("complete")
    print("Max Altitude: ", test_flight.apogee, "m or", test_flight.apogee*3.28084, "ft")
   
    plt.show(block=True)
