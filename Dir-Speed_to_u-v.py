import pandas as pd
import numpy as np
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

def convert_to_uv(input_file, output_file):
    # 1. Resolve paths and load the CSV file
    in_path = os.path.join(script_dir, input_file)
    out_path = os.path.join(script_dir, output_file)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    df = pd.read_csv(in_path)
    
    # Strip any hidden spaces from columns just to be safe
    df.columns = df.columns.str.strip()
    
    # Ensure the columns exist before doing math
    required = ['h', 'theta', 'speed']
    if not all(col in df.columns for col in required):
        print(f"Error: Expected columns {required} in {input_file}, found {list(df.columns)}")
        return

    # 2. Convert degrees to radians for numpy trig functions
    theta_rad = np.radians(df['theta'])
    
    # 3. Calculate u and v components
    # STANDARD MATH CONVERSION: 
    # (Use this if 0 degrees is East, 90 is North, and wind is going TO the direction)
    df['u'] = df['speed'] * np.cos(theta_rad)
    df['v'] = df['speed'] * np.sin(theta_rad)
    
    # METEOROLOGICAL CONVERSION:
    # (If your data uses Weather conventions where 0 degrees is North and wind is coming FROM that direction, 
    # comment out the two lines above and uncomment the two lines below!)
    # df['u'] = -df['speed'] * np.sin(theta_rad)
    # df['v'] = -df['speed'] * np.cos(theta_rad)
    
    # 4. Filter the dataframe to only keep h, u, and v
    df_final = df[['h', 'u', 'v']]
    
    # Save to CSV
    df_final.to_csv(out_path, index=False)
    print(f"Successfully converted {in_path} and saved to {out_path}")

# --- Example Usage ---
# Pass in the transformed files created by DayGenerator.py


def loopct_uv(input_file, output_file):
    for i in range(100):
        input = input_file + str(i) + '.csv'
        output = output_file + str(i) + '.csv'
        convert_to_uv(input, output)

# convert_to_uv('TestGeneration/Fast/FastDay_transformed', 'TestGeneration/FastUV/FastDay_UV')
# convert_to_uv('TestGeneration/Slow/Slowday_transformed', 'TestGeneration/SlowUV/Slowday_UV')
loopct_uv('TestGeneration/Fast/FastDay_transformed', 'TestGeneration/FastUV/FastDay_UV')
loopct_uv('TestGeneration/Slow/Slowday_transformed', 'TestGeneration/SlowUV/Slowday_UV')