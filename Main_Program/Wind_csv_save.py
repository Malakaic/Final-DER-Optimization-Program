import os
import requests
import pandas as pd
import numpy as np
import time
import config


# Cache dictionary to hold previously fetched results


def wind_function_main(self, latitude, longitude, turbine_name_user, turbine_capacity_user, rotor_diameter_user, turbine_efficiency_user):
    # Check if latitude and longitude are valid
    if not (isinstance(latitude, (int, float)) and isinstance(longitude, (int, float))):
        raise ValueError("Latitude and longitude must be numeric.")


    # Definitions for API key
    lon = longitude
    lat = latitude

    wind_data_type = "windspeed_100m"
    year = 2023
    user_email = "malakaicrane@gmail.com"
    api_key = "YT5auN6kF3hMbh7c1bQeyKCZYssN2DH0sv3zmZpG"

    turbine_name = turbine_name_user
    turbine_capacity = turbine_capacity_user
    rotor_diameter = rotor_diameter_user
    turbine_efficiency = turbine_efficiency_user

    # Set the folder path for "Environmental Data"
    folder_name = config.project_name
    project_dir = os.getcwd()
    folder_path = os.path.join(project_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Define file paths
    wind_speed_file = os.path.join(folder_path, f"{turbine_name}_wind_data_saved.csv")

    # Download the CSV data (always overwrite)
    download_wind_csv(lon, lat, wind_data_type, year, user_email, api_key, wind_speed_file)

    # Calculate wind power from CSV and add a column for power output
    total_power = calculate_wind_power_with_columns(wind_speed_file, turbine_capacity, turbine_efficiency, rotor_diameter)


    return total_power


def download_wind_csv(lon, lat, wind_data_type, year, user_email, api_key, wind_speed_file):
    """
    Downloads CSV data from the given API URL and saves it to the 'Environmental Data' folder.
    """
    api_url = f"https://developer.nrel.gov/api/wind-toolkit/v2/wind/wtk-bchrrr-v1-0-0-download.csv?wkt=POINT({lon} {lat})&attributes={wind_data_type}&names={year}&utc=false&leap_day=true&email={user_email}&api_key={api_key}"
    
    try:
        time.sleep(2)
        response = requests.get(api_url)
        
        # Check if the response is successful
        if response.status_code == 200:
            with open(wind_speed_file, 'wb') as file:
                file.write(response.content)
            print(f"Data successfully downloaded and saved to {wind_speed_file}")
        else:
            print(f"Failed to download data. HTTP Status Code: {response.status_code}")
            print(f"Error Details: {response.text}")
    except Exception as e:
        print(f"An error occurred while downloading wind data: {e}")

def calculate_wind_power_with_columns(wind_speed_file, turbine_capacity, turbine_efficiency, rotor_diameter):
    """
    Reads wind speed data from a CSV file, calculates power output, and adds a column for power output.
    """
    try:
        # Read CSV, skipping irrelevant rows and limiting the amount of data read
        df = pd.read_csv(wind_speed_file, skiprows=1, usecols=lambda column: column not in ['Unnamed: 0'])

        # Check for necessary columns and extract wind speed
        required_columns = ['Year', 'Month', 'Day', 'Hour', 'Minute']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"The column '{col}' is missing from the data.")

        wind_speed_column = next((col for col in df.columns if "wind speed" in col.lower()), None)
        if not wind_speed_column:
            raise ValueError("Wind speed column not found in the data.")

        # Convert wind speed column to numeric
        df['wind_speed'] = pd.to_numeric(df[wind_speed_column], errors='coerce')

        # Calculate power output only for valid entries
        air_density = 1.225  # kg/m^3
        swept_area = np.pi * (rotor_diameter / 2) ** 2  # m^2
        
        # Calculate power output and apply capacity limits in one go
        df['power_output'] = np.minimum(
            0.5 * air_density * swept_area * (df['wind_speed'] ** 3) * (turbine_efficiency / 1000),
            turbine_capacity
        )

        # Save the updated DataFrame back to the same CSV file
        df.to_csv(wind_speed_file, index=False)

        print(f"Detailed wind power output saved to: {wind_speed_file}")

        # Calculate and print total power output
        total_power_kwh = df['power_output'].sum()
        print(f"Total wind power produced: {total_power_kwh:.2f} kWh")
        return total_power_kwh
    
    except Exception as e:
        print(f"An error occurred while calculating wind power: {e}")