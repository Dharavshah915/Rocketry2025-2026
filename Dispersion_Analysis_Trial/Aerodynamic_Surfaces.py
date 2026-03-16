import rocketpy
from pathlib import Path
ROOT = Path(__file__).resolve().parent

air_foil_shape = ROOT/ "Files" / "AirFoilShape" / "NACA0012-radians.txt"

def define_surfaces(rocket):
    nose_cone = rocket.add_nose(length=0.55829, kind="vonKarman", position=1.278)

    # IMPORTANT: modify the file path below to match your own system
    fin_set = rocket.add_trapezoidal_fins(
        n=4,
        root_chord=0.254,
        tip_chord=0.09525,
        span=0.120650,
        position=-1.04956,
        cant_angle=0,
        airfoil=(air_foil_shape, "radians"),
    )

    tail = rocket.add_tail(
        top_radius=0.0635, bottom_radius=0.0435, length=0.060, position=-1.194656
    )
