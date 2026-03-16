import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
from matplotlib.patches import Ellipse
from datetime import datetime
import datetime as dt
from numpy.random import normal, choice, uniform
from rocketpy import Environment, SolidMotor, Rocket, Flight, Function
import copy
from pathlib import Path

import Motor
# import Rocket
import RandomRocket
import ParachuteWithLag
import ExternalEnviornmentalFactorsSetupAltered as Envi
import Aerodynamic_Surfaces as As

# --- 3. ANALYSIS PARAMETERS (Uncertainties) ---
analysis_parameters = {
    "wind_speed_scale_range": (0.7, 1.3),  # Scale GFS wind speed by 70%-130% (varies speed, keeps profile)
    "wind_direction_variation": 30,        # ±30° variation around GFS direction (creates ellipse)
    # If you want rocket mass to be fixed (non-variable), use a plain number:
    "rocketMass": 14.426,
    # If you want rocket mass to be variable, use (mean, stddev) instead:
    # "rocketMass": (14.426, 0.1),       # Mean, Std Dev
    #"inclination": (85, 1.5),         # Launch rail angle
    "heading": 225,              # Launch rail heading range (deg)
    "lag_rec": 0.5,            # Parachute delay
    # "ensembleMember": [0, 1, 2, 3]    # Discrete weather choices
}

# Export functions
def flight_settings_generator(parameters, total_number):
    for i in range(total_number):
        setting = {}
        
        for key, value in parameters.items():
            # Skip non-flight parameters that are used in the loop
            if key in ["wind_speed_scale_range", "wind_direction_variation"]:
                continue
                
            if isinstance(value, tuple):
                if "range" in key or key == "heading":
                    # Other ranges: uniform sampling
                    setting[key] = uniform(value[0], value[1])
                else:
                    # Normal distribution (Mean, StdDev)
                    setting[key] = normal(value[0], value[1])
            elif isinstance(value, (list, np.ndarray)):
                setting[key] = choice(value)
            else:
                # Fixed constant (e.g., rocketMass: 14.426)
                setting[key] = value
        
        # Add wind scaling and direction variation for this flight
        scale_range = parameters.get("wind_speed_scale_range", (1.0, 1.0))
        setting["wind_scale"] = uniform(scale_range[0], scale_range[1])
        
        dir_var = parameters.get("wind_direction_variation", 0)
        setting["direction_offset"] = uniform(-dir_var, dir_var)
        
        yield setting

def export_flight_data(setting, flight_data):
    # Extracts the specific results we need for the ellipses
    return {
        "impactX": flight_data.x_impact,
        "impactY": flight_data.y_impact,
        "apogee": flight_data.apogee - 250  # ELEVATION constant
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

# --- 1. PREPARE THE WEATHER (OUTSIDE THE LOOP) ---
print("Downloading base GFS forecast...")
base_env = Envi.get_base_forecast()
print("✓ Forecast loaded")

# We'll vary wind speed in the loop using the wind_speed_range parameter
use_dataset = False  # Simple mode: vary winds on the fly

# --- 2. Sim Loop
num_simulations = 50
results = []
progress_every = 25
failed_sims = 0

print(f"Starting Monte Carlo for {num_simulations} flights...")

# Create Motor (constant, build once)
motor = Motor.define_motor()

for sim_idx, setting in enumerate(flight_settings_generator(analysis_parameters, num_simulations), start=1):
    try:
        # Create a FRESH rocket for each simulation to avoid state accumulation
        rocket = RandomRocket.define_rocket(mass=setting.get("rocketMass", analysis_parameters["rocketMass"]))
        rocket.add_motor(motor, position=-1.0)
        Main, Drouge = ParachuteWithLag.add_parachutes(rocket, lag=setting.get("lag_rec", analysis_parameters["lag_rec"]))
        As.define_surfaces(rocket)

        # Create environment and apply wind variations for this simulation
        Env = copy.deepcopy(base_env)
        
        # Get wind scaling and direction offset for this flight
        wind_scale = setting["wind_scale"]
        direction_offset = setting["direction_offset"]
        
        # Get original wind functions from GFS (altitude-varying)
        original_wind_x = Env.wind_velocity_x
        original_wind_y = Env.wind_velocity_y
        
        # Calculate ground wind for reporting
        base_wind_x = original_wind_x(0)
        base_wind_y = original_wind_y(0)
        base_ground_wind = np.sqrt(base_wind_x**2 + base_wind_y**2)
        base_heading = np.degrees(np.arctan2(base_wind_y, base_wind_x))
        
        # Apply wind variations while keeping altitude-varying profile:
        # 1. Scale wind speed (multiply entire profile)
        # 2. Rotate wind direction (apply to entire profile)
        angle_offset_rad = np.radians(direction_offset)
        cos_offset = np.cos(angle_offset_rad)
        sin_offset = np.sin(angle_offset_rad)
        
        # Create closure functions (must capture variables explicitly)
        def create_wind_x(ox, oy, scale, cos_a, sin_a):
            return lambda h: (ox(h) * cos_a - oy(h) * sin_a) * scale
        
        def create_wind_y(ox, oy, scale, cos_a, sin_a):
            return lambda h: (ox(h) * sin_a + oy(h) * cos_a) * scale
        
        # Create new wind functions that scale AND rotate the GFS profile
        Env.wind_velocity_x = Function(
            create_wind_x(original_wind_x, original_wind_y, wind_scale, cos_offset, sin_offset)
        )
        Env.wind_velocity_y = Function(
            create_wind_y(original_wind_x, original_wind_y, wind_scale, cos_offset, sin_offset)
        )
        
        # Calculate actual applied wind for reporting
        actual_wind_x = Env.wind_velocity_x(0)
        actual_wind_y = Env.wind_velocity_y(0)
        actual_ground_wind = np.sqrt(actual_wind_x**2 + actual_wind_y**2)
        actual_heading = np.degrees(np.arctan2(actual_wind_y, actual_wind_x))
        
        if sim_idx <= 3:
            print(f"  GFS base: {base_ground_wind:.2f} m/s @ {base_heading:.0f}°")
            print(f"  Applied: {actual_ground_wind:.2f} m/s @ {actual_heading:.0f}° (scale={wind_scale:.2f}, offset={direction_offset:.0f}°)")

        # Run Flight
        TestFlight = Flight(
            rocket=rocket, 
            environment=Env, 
            rail_length=3.6576, # in meters (12 feet) (may need altering)
            inclination=90-4,  #relative to the ground
            heading=setting["heading"],        
            verbose=False
        )
        
        # Diagnostic: Print key metrics for first few flights
        if sim_idx <= 3:
            print(f"    Parachutes={len(rocket.parachutes)}, "
                  f"Impact velocity={TestFlight.impact_velocity:.1f} m/s")
            print(f"    Time={TestFlight.t_final:.1f}s, "
                  f"Apogee={TestFlight.apogee:.1f}m")
            print(f"    Impact: X={TestFlight.x_impact:.1f}m, Y={TestFlight.y_impact:.1f}m")
            print(f"    Parachute events: {len(TestFlight.parachute_events)}")
        
        # Extract data immediately
        results.append(export_flight_data(setting, TestFlight))
        
        # Clean up Flight object to free memory
        del TestFlight
        del rocket
        del Env
        
        # Progress reporting
        if sim_idx == 1 or (sim_idx % progress_every) == 0 or sim_idx == num_simulations:
            mass = setting.get("rocketMass", None)
            mass_str = f"{mass:.2f} kg" if isinstance(mass, (int, float)) else "N/A"
            print(f"Simulating Flight {sim_idx}/{num_simulations} | Mass: {mass_str}")

    except Exception as e:
        print(f"Simulation {sim_idx} failed: {e}")
        failed_sims += 1

# --- 6. PLOTTING THE ERROR ELLIPSES ---
print(f"\n{'='*70}")
print(f"SIMULATION RESULTS")
print(f"{'='*70}")
print(f"Total simulations attempted: {num_simulations}")
print(f"Successful: {len(results)}")
print(f"Failed: {failed_sims}")
print(f"{'='*70}")

impact_x = [r["impactX"] for r in results]
impact_y = [r["impactY"] for r in results]

# Weather statistics
print(f"\n{'='*70}")
print(f"WIND PARAMETERS")
print(f"{'='*70}")
scale_range = analysis_parameters.get('wind_speed_scale_range', (1.0, 1.0))
dir_var = analysis_parameters.get('wind_direction_variation', 0)
print(f"Wind speed: GFS profile scaled by {scale_range[0]:.1f}x to {scale_range[1]:.1f}x")
print(f"Wind direction: GFS direction ± {dir_var:.0f}°")
print(f"Altitude profile: GFS altitude-varying winds PRESERVED ✓")

# Calculate and print dispersion statistics
radial_distances = [np.sqrt(x**2 + y**2) for x, y in zip(impact_x, impact_y)]
mean_distance = np.mean(radial_distances)
std_distance = np.std(radial_distances)
max_distance = np.max(radial_distances)
min_distance = np.min(radial_distances)

print(f"\n{'='*70}")
print("DISPERSION STATISTICS")
print(f"{'='*70}")
print(f"Mean radial distance: {mean_distance:.1f} m")
print(f"Std dev: {std_distance:.1f} m")
print(f"Min distance: {min_distance:.1f} m")
print(f"Max distance: {max_distance:.1f} m")
print(f"Range: {max_distance - min_distance:.1f} m")

fig, ax = plt.subplots(figsize=(10, 8))
# Use edgecolors to show overlapping points better
ax.scatter(impact_x, impact_y, s=30, facecolors='red', edgecolors='black', 
           linewidths=0.5, label=f'Impact Points (n={len(results)})', alpha=0.7)


draw_error_ellipse(impact_x, impact_y, ax, n_std=1.513, edgecolor='red', lw=2, label=r'1$\sigma$ (68.2%)')
draw_error_ellipse(impact_x, impact_y, ax, n_std=2.482, edgecolor='blue', lw=2, label=r'2$\sigma$ (95.4%)')
#draw_error_ellipse(impact_x, impact_y, ax, n_std=3, edgecolor='green', lw=2, label=r'3$\sigma$ (99%)')

ax.axhline(0, color='black', lw=1); ax.axvline(0, color='black', lw=1)

# Title
scale_range = analysis_parameters.get('wind_speed_scale_range', (1.0, 1.0))
dir_var = analysis_parameters.get('wind_direction_variation', 0)
title_text = f"Monte Carlo Landing Dispersion\n({num_simulations} Flights, GFS Winds: {scale_range[0]:.1f}-{scale_range[1]:.1f}x Speed, ±{dir_var:.0f}° Direction)"
filename = "dispersion_analysis.png"

ax.set_title(title_text)
ax.set_xlabel("Impact X (m)"); ax.set_ylabel("Impact Y (m)")
ax.legend(); ax.set_aspect('equal', 'datalim'); plt.grid(True)

# Save plot to file
output_path = Path(__file__).resolve().parent / filename
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\nPlot saved to: {output_path}")
plt.show()
