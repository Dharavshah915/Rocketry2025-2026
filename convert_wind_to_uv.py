import pandas as pd
import numpy as np
import os
import glob

def batch_convert_wind(source_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    files = glob.glob(os.path.join(source_folder, "*.csv"))
    
    if not files:
        print(f"No CSV files found in {source_folder}")
        return

    print(f"Found {len(files)} files. Starting conversion...")

    for file_path in files:
        filename = os.path.basename(file_path)
        try:
            df = pd.read_csv(file_path)
            
            h_col = 'geopotential height_m'
            dir_col = 'wind direction_degree'
            spd_col = 'wind speed_m/s'

            # 1. Force columns to numeric (converts strings to NaN)
            for col in [h_col, dir_col, spd_col]:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # 2. Drop rows with NaN (including the ones we just forced)
            df = df.dropna(subset=[h_col, dir_col, spd_col])

            # 3. Discard rows where any of these values are exactly 0
            # This handles your "if 0 discard the row" requirement
            df = df[(df[h_col] != 0) & (df[dir_col] != 0) & (df[spd_col] != 0)]

            # 4. Conversion Math
            rads = np.radians(df[dir_col])
            df['u'] = -df[spd_col] * np.sin(rads)
            df['v'] = -df[spd_col] * np.cos(rads)
            
            final_df = df[[h_col, 'u', 'v']].rename(columns={h_col: 'height'})
            
            save_path = os.path.join(output_folder, f"transformed_{filename}")
            final_df.to_csv(save_path, index=False)
            print(f" Successfully processed: {filename}")
            
        except Exception as e:
            print(f" Error processing {filename}: {e}")

batch_convert_wind('NewAlteredCSV', 'transformedWindData')