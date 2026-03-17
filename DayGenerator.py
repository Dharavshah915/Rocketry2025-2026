import pandas as pd
import numpy as np
import os

script_dir = os.path.dirname(os.path.abspath(__file__))


def find_cols(df):
    cols = {c.lower(): c for c in df.columns}
    speed_col = None
    dir_col = None
    height_col = None
    for low, real in cols.items():
        if "speed" in low:
            speed_col = real
        if "theta" in low or "dir" in low:
            dir_col = real
        if low in ("h", "height") or "height" in low:
            height_col = real
    return height_col, dir_col, speed_col


def transform_wind_data(input_file, output_file, a, b, c, d):
    # 1. Resolve paths and load the CSV file
    in_path = os.path.join(script_dir, input_file)
    out_path = os.path.join(script_dir, output_file)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df = pd.read_csv(in_path)

    height_col, dir_col, speed_col = find_cols(df)
    if not all([height_col, dir_col, speed_col]):
        raise ValueError(f"Could not find required columns in {in_path}. Found: {list(df.columns)}")

    # Ensure columns are numeric (ignoring any empty rows/errors)
    df[speed_col] = pd.to_numeric(df[speed_col], errors='coerce')
    df[dir_col] = pd.to_numeric(df[dir_col], errors='coerce')
    
    # ---------------- WIND SPEED ----------------
    # Multiply wind speed by 'a'
    df[speed_col] = df[speed_col] * a
    
    # Generate random numbers between -b and b for every row
    random_b = np.random.uniform(-b, b, size=len(df))
    df[speed_col] = df[speed_col] + random_b
    
    # ---------------- DIRECTION ----------------
    # Add 'c' to all directions
    df[dir_col] = df[dir_col] + c
    
    # Generate random numbers between -d and d for every row
    random_d = np.random.uniform(-d, d, size=len(df))
    df[dir_col] = df[dir_col] + random_d
    
    # OPTIONAL: If you want to force the direction to stay within a 0-360 degree circle, 
    # you can uncomment the line below:
    # df[dir_col] = df[dir_col] % 360
    
    # Rename to standardized columns h, theta, speed
    df_standard = df.rename(
        columns={
            height_col: "h",
            dir_col: "theta",
            speed_col: "speed",
        }
    )[["h", "theta", "speed"]]

    # Save the transformed data to a new CSV file
    df_standard.to_csv(out_path, index=False)
    print(f"Successfully processed {in_path} and saved to {out_path}")

def looptwd(input_file, output_file, a, b, c, d):
    for i in range(100):
        c =np.random.uniform(0,360)
        a = np.random.normal(1,0.5)  #first param is mu (u), second is std
        b = np.random.normal(0.2, 0.5)
        d = np.random.normal(1,3)
        output = output_file + str(i) + '.csv'
        transform_wind_data(input_file, output, a, b, c, d)

# --- Example Usage ---
# Set your parameters here:
a = 1  # Multiply wind speed by 1.2
b = 0.8  # Add a random value between -2.0 and 2.0 to wind speed
c = 130   # Add 50 degrees to direction
d = 1  # Add a random value betweena -5.0 and 5.0 to direction

# Run the function on your files (paths now resolved relative to this script)
looptwd('2FilesFromTeamsFiltered/Fast/FastDay.csv', 'TestGeneration/Fast/FastDay_transformed', a, b, c, d)
looptwd('2FilesFromTeamsFiltered/Slow/Slowday.csv', 'TestGeneration/Slow/Slowday_transformed', a, b, c, d)
# transform_wind_data('2FilesFromTeamsFiltered/Fast/FastDay.csv', 'TestGeneration/Fast/FastDay_transformed.csv', a, b, c, d)
# transform_wind_data('2FilesFromTeamsFiltered/Slow/Slowday.csv', 'TestGeneration/Slow/Slowday_transformed.csv', a, b, c, d)