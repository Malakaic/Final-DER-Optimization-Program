import os
import requests
import pandas as pd
import numpy as np
import json
import time
import config

#cache = {}


def solar_function(self, latitude, longitude, pv_name_user, system_capacity_user, module_type_user):
    # API Parameter Definitions
    print("Solar Function Called")
    # Check if latitude and longitude are valid
    if not (isinstance(latitude, (int, float)) and isinstance(longitude, (int, float))):
        raise ValueError("Latitude and longitude must be numeric.")

    api_key = "YT5auN6kF3hMbh7c1bQeyKCZYssN2DH0sv3zmZpG"
    lat = latitude
    lon = longitude
    
    pv_name = pv_name_user
    system_capacity = system_capacity_user
    module_type = module_type_user

    # Convert module type to a numeric value for the dictionary
    """
    module_type_value = 0
    if module_type == "Monocrystalline":
        module_type_value = 0
    elif module_type == "Polycrystalline":
        module_type_value = 1
    elif module_type == "Thin-Film":
        module_type_value = 2
    """                    
    azimuth = 180  # Azimuth angle in degrees - Required
    tilt = 20  # Tilt angle in degrees - Required
    losses = 10  # System losses as a percentage - Required
    array_type = 1  # Fixed array type - Required (0 = fixed - open rack, 1 = fixed - roof mount, 2 = 1-axis, 3 = 1-axis backtracking, 4 = 2-axis )

    dataset = "nsrdb"  # Dataset to use - TMY data

    # Set the folder path for "Environmental Data"
    folder_name = config.project_name
    project_dir = os.getcwd()
    folder_path = os.path.join(project_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Define file paths
    solar_data_file = os.path.join(folder_path, f"{pv_name}_solar_data_saved.csv")

    # Download the CSV data (always overwrite)
    download_solar_csv(api_key, lat, lon, system_capacity, azimuth, tilt, losses, array_type, module_type, dataset, solar_data_file, pv_name)

def download_solar_csv(api_key, lat, lon, system_capacity, azimuth, tilt, losses, array_type, module_type, dataset, solar_data_file, pv_name):
    """
    Downloads CSV data from the given API URL and saves it to the 'Environmental Data' folder.
    """
    print(f"Downloading solar data for PV: {pv_name}")
    api_url = f"https://developer.nrel.gov/api/pvwatts/v8.csv"

    # API request parameters
    params = {
        "api_key": api_key,
        "lat": lat,
        "lon": lon,
        "system_capacity": system_capacity,
        "azimuth": azimuth,
        "tilt": tilt,
        "losses": losses,
        "array_type": array_type,
        "module_type": module_type,
        "dataset": dataset,
        "timeframe": "hourly"  # Request hourly data
    }

    try:
        time.sleep(2)
        response = requests.get(api_url, params=params)
        
        # Check if the response is successful
        if response.status_code == 200:
            with open(solar_data_file, 'wb') as file:
                file.write(response.content)
            print(f"Data successfully downloaded and saved to {solar_data_file}")
        else:
            print(f"Failed to download data. HTTP Status Code: {response.status_code}")
            print(f"Error Details: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

