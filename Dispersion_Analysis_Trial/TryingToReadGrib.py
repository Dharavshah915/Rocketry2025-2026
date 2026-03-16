import xarray as xr
import os
import numpy as np
import glob

# 1. Setup Directories
script_dir = os.path.dirname(os.path.abspath(__file__))
input_folder = os.path.join(script_dir, "GRIBS")
output_folder = os.path.join(script_dir, "csv_output")

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# 2. Find all .grib files
grib_files = glob.glob(os.path.join(input_folder, "*.grib"))

if not grib_files:
    print(f"No .grib files found in {input_folder}. Please check the path!")

for file_path in grib_files:
    filename = os.path.basename(file_path)
    print(f"Processing: {filename}...")
    
    try:
        # 3. Open the GRIB
        # Using cfgrib engine as discussed for high-fidelity weather data
        ds = xr.open_dataset(
            file_path, 
            engine='cfgrib',
            backend_kwargs={'filter_by_keys': {'typeOfLevel': 'isobaricInhPa'}}
        )

        # 4. Average across all Latitudes and Longitudes
        # This creates the vertical profile needed for RocketPy
        ds_averaged = ds[['u', 'v']].mean(dim=['latitude', 'longitude'])

        # 5. Extract values and convert Pressure to Height (m)
        u_avg = ds_averaged.u.values
        v_avg = ds_averaged.v.values
        p_levels = ds_averaged.isobaricInhPa.values
        
        # Standard barometric formula for altitude
        h_avg = 44330 * (1 - (p_levels / 1013.25)**0.1903)

        # 6. Build and Sort Table (Ground -> Space)
        wind_table = np.column_stack((h_avg, u_avg, v_avg))
        wind_table = wind_table[wind_table[:, 0].argsort()]

        # 7. Save to CSV
        output_filename = filename.replace(".grib", ".csv")
        save_path = os.path.join(output_folder, output_filename)
        
        np.savetxt(
            save_path, 
            wind_table, 
            delimiter=",", 
            header="height,u,v", 
            comments=""
        )
        
        print(f"   Saved to: {output_filename}")
        
        # Close dataset to free up memory for the next file
        ds.close()

    except Exception as e:
        print(f"   Error processing {filename}: {e}")

print("\nAll files processed.")