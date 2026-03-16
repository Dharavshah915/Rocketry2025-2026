import rocketpy
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
print("ROOT =", ROOT)
thrust_file = ROOT / "Files" / "Motor_Thrust_Curves" / "Cesaroni_21062O3400-P.eng"
thrust_data = np.loadtxt(thrust_file, skiprows=3)

def define_motor(thrust_data=thrust_data):
    motor = rocketpy.SolidMotor(
        thrust_source=thrust_data,
        dry_mass=5.912,  #Dry Mass = Total Loaded Mass - Propellant Mass
        dry_inertia=(0.125, 0.125, 0.002),
        nozzle_radius=0.033,
        grain_number=6,
        grain_density=1815,
        grain_outer_radius=33 / 1000,
        grain_initial_inner_radius=15 / 1000,
        grain_initial_height= 0.155,
        grain_separation=0.005,
        grains_center_of_mass_position=0.450,
        center_of_dry_mass_position=0.350,
        nozzle_position=0,
        burn_time=6.16,
        throat_radius= 0.011,
        interpolation_method="linear",
        coordinate_system_orientation="nozzle_to_combustion_chamber",
    )
    #motor.info()
    return motor

