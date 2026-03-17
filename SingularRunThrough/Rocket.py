import rocketpy
from pathlib import Path
import numpy as np
#
ROOT = Path(__file__).resolve().parent
print("ROOT =", ROOT)
off = ROOT / "Files" / "dispersion_analysis_inputs" / "powerOffDragCurve2026.csv"
on = ROOT / "Files" / "dispersion_analysis_inputs" / "powerOnDragCurve2026.csv"

def define_rocket(off=off, on=on, mass=14.426, upper_rail_button=1.289558, lower_rail_button=0.06985, angle=45): # set defultws 
    calisto = rocketpy.Rocket(
    radius=127 / 2000,
    mass=mass,
    inertia=(20.969, 20.969, 0.051),
    power_off_drag=off,
    power_on_drag=on,
    center_of_mass_without_motor=0,
    coordinate_system_orientation="tail_to_nose",
    )
    rail_buttons = calisto.set_rail_buttons(
    upper_button_position=upper_rail_button,
    lower_button_position=lower_rail_button,
    angular_position=angle,  
    )   
    return calisto


