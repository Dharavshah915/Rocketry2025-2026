import os
import xarray as xr
import numpy as np

script_dir = os.path.dirname(os.path.abspath(__file__))
grib_path = os.path.join(script_dir, "GRIBS", "nam_218_20231126_1800_006.grb2")

# Load u and v separately (avoids the 43 vs 41 level conflict)
ds_u = xr.open_dataset(
    grib_path, engine='cfgrib',
    backend_kwargs={'filter_by_keys': {'typeOfLevel': 'isobaricInhPa', 'shortName': 'u'}}
)
ds_v = xr.open_dataset(
    grib_path, engine='cfgrib',
    backend_kwargs={'filter_by_keys': {'typeOfLevel': 'isobaricInhPa', 'shortName': 'v'}}
)

# Merge into one dataset
ds = xr.merge([ds_u, ds_v])
ds_u.close()
ds_v.close()

# Extract wind profile
p_levels = ds.isobaricInhPa.values
u = ds['u'].mean(dim=['y', 'x']).values
v = ds['v'].mean(dim=['y', 'x']).values
h = 44330 * (1 - (p_levels / 1013.25)**0.1903)

wind_profile = np.column_stack((h, u, v))
wind_profile = wind_profile[wind_profile[:, 0].argsort()]
print(wind_profile)