import xarray as xr
import numpy as np

# 1. Open the GRIB
ds = xr.open_dataset(
    'your_data.grib', 
    engine='cfgrib',
    backend_kwargs={'filter_by_keys': {'typeOfLevel': 'isobaricInhPa'}}
)

# 2. Average across all Latitudes and Longitudes
# This reduces the 3D grid (P, Lat, Lon) to a 1D profile (P)
ds_averaged = ds[['u', 'v']].mean(dim=['latitude', 'longitude'])

# 3. Extract the averaged values
u_avg = ds_averaged.u.values
v_avg = ds_averaged.v.values
p_levels = ds_averaged.isobaricInhPa.values

# 4. Convert Pressure to Height (m)
h_avg = 44330 * (1 - (p_levels / 1013.25)**0.1903)

# 5. Build the final NumPy Table
wind_table = np.column_stack((h_avg, u_avg, v_avg))

# 6. Sort by height (Ground -> Space)
wind_table = wind_table[wind_table[:, 0].argsort()]

# 7. Normalize height so the launch site starts at 0m
wind_table[:, 0] -= wind_table[0, 0]

print("Averaged Wind Table (Ground-Relative):")
print(wind_table)