
def add_parachute_main(rocket, lag):
    Main = rocket.add_parachute(
        "Main",
        cd_s=2.2,
        trigger=800,
        sampling_rate=105,
        lag=lag,
        noise=(0, 8.3, 0.5),
    )
    return Main

def add_parachute_drogue(rocket, lag):
    Drogue = rocket.add_parachute(
        "Drogue",
        cd_s=0.97,
        trigger="apogee",
        sampling_rate=105,
        lag=lag,
        noise=(0, 8.3, 0.5),
    )
    return Drogue

def add_parachutes(rocket, lag):
    Main = add_parachute_main(rocket, lag)
    Drouge = add_parachute_drogue(rocket, lag)
    return Main, Drouge


#can be used to remove parachautes 

    #Calisto.parachutes.remove(Drogue)
    #Calisto.parachutes.remove(Main)