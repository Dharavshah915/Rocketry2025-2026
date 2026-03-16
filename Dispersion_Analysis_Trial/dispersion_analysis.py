import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
from matplotlib.patches import Ellipse
from datetime import datetime
import datetime as dt
from numpy.random import normal, choice, uniform
from rocketpy import Environment, SolidMotor, Rocket, Flight, Function
from pathlib import Path

import Motor
# import Rocket
import RandomRocket
import ParachuteWithLag
import ExternalEnviornmentalFactorsSetupAltered as Envi
import Aerodynamic_Surfaces as As

# --- 3. ANALYSIS PARAMETERS (Uncertainties) ---
analysis_parameters = {
    "rocketMass": 14.426,
    "heading": 0,  # Launch rail heading range (deg)
    "lag_rec": 0.5,  # Parachute delay
}

# Export functions
def flight_settings_generator(parameters, total_number):
    for i in range(total_number):
        setting = {}
        
        for key, value in parameters.items():
            if isinstance(value, tuple):
                # Uniform sampling for ranges (wind_speed, wind_heading, heading)
                setting[key] = uniform(value[0], value[1])
            elif isinstance(value, (list, np.ndarray)):
                setting[key] = choice(value)
            else:
                # Fixed constant (e.g., rocketMass: 14.426)
                setting[key] = value
        
        yield setting

def export_flight_data(flight_data):
    # add settings here if tyou want to keep setting data to filter by wind later on
    # Extracts the specific results we need for the ellipses
    return {
        "impactX": flight_data.x_impact,
        "impactY": flight_data.y_impact,
        "apogee": flight_data.apogee - Env.elevation  # ELEVATION constant
    }

def draw_error_ellipse(x, y, ax, n_std=2.0, facecolor='none', **kwargs):
    """Calculates and draws the statistical probability ellipse"""
    cov = np.cov(x, y)
    pearson = cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])
    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2,
                      facecolor=facecolor, **kwargs)
    scale_x = np.sqrt(cov[0, 0]) * n_std
    scale_y = np.sqrt(cov[1, 1]) * n_std
    transf = transforms.Affine2D().rotate_deg(45).scale(scale_x, scale_y).translate(np.mean(x), np.mean(y))
    ellipse.set_transform(transf + ax.transData)
    return ax.add_patch(ellipse)


# --- 2. Setup Environment and Motor
print("Setting up environment...")

# --- GFU 
Envio = Envi.NOAA_Sucks_Weather()
print("Environment ready")

# setting up custom weather + GFU
Env = Envio
# Env = Envi.use_chosen_day(Envio)
# print("Custom weather ready")


# Create Motor (constant, build once)
motor = Motor.define_motor()

# --- 3. Sim Loop
num_simulations = 5
results = []
failed_sims = 0

print(f"Starting Monte Carlo for {num_simulations} flights...")

for sim_idx, setting in enumerate(flight_settings_generator(analysis_parameters, num_simulations), start=1):
    try:
        # Create a FRESH rocket for each simulation to avoid state accumulation
        rocket = RandomRocket.define_rocket(mass=setting.get("rocketMass", analysis_parameters["rocketMass"]))
        rocket.add_motor(motor, position=-1.0)
        Main, Drouge = ParachuteWithLag.add_parachutes(rocket, lag=setting.get("lag_rec", analysis_parameters["lag_rec"]))
        As.define_surfaces(rocket)

        # Run Flight
        TestFlight = Flight(
            rocket=rocket, 
            environment=Env, 
            rail_length=3.6576, # in meters (12 feet) (may need altering)
            inclination=90-4,  #relative to the ground
            heading=setting["heading"],        
            verbose=False
        )
        
        # Extract data immediately, you will need to store data as well if you want
        # to filter data by wind later rather than before
        # results.append(export_flight_data(setting, TestFlight))
        results.append(export_flight_data(TestFlight))
        
        # Clean up Flight object to free memory
        del TestFlight
        del rocket
        
        # Print completion for each simulation
        print(f"Simulation {sim_idx}/{num_simulations} completed")

    except Exception as e:
        print(f"Simulation {sim_idx} failed: {e}")
        failed_sims += 1

# --- 6. PLOTTING THE ERROR ELLIPSES ---
impact_x = [r["impactX"] for r in results]
impact_y = [r["impactY"] for r in results]

fig, ax = plt.subplots(figsize=(10, 8))
# Use edgecolors to show overlapping points better
ax.scatter(impact_x, impact_y, s=30, facecolors='black', edgecolors='black', 
           linewidths=0.5, label=f'Impact Points (n={len(results)})', alpha=0.7)


draw_error_ellipse(impact_x, impact_y, ax, n_std=1.513, edgecolor='red', lw=2, label=r'1$\sigma$ (68.2%)')
draw_error_ellipse(impact_x, impact_y, ax, n_std=2.482, edgecolor='blue', lw=2, label=r'2$\sigma$ (95.4%)')
#draw_error_ellipse(impact_x, impact_y, ax, n_std=3, edgecolor='green', lw=2, label=r'3$\sigma$ (99%)')

ax.axhline(0, color='black', lw=1); ax.axvline(0, color='black', lw=1)

# Title
title_text = f"Monte Carlo Landing Dispersion\n({num_simulations} Flights, GFS Forecast)"
filename = "dispersion_analysis.png"

ax.set_title(title_text)
ax.set_xlabel("Impact X (m)"); ax.set_ylabel("Impact Y (m)")
ax.legend(); ax.set_aspect('equal', 'datalim'); plt.grid(True)

# Save plot to file
output_path = Path(__file__).resolve().parent / filename
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\nPlot saved to: {output_path}")
plt.show()
