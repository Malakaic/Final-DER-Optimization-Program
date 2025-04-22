"""
pip install openmeteo-requests
pip install requests-cache retry-requests numpy pandas
https://open-meteo.com/en/terms
"""

import os
import pandas as pd
import numpy as np
import time
import config
import datetime

import openmeteo_requests
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


def wind_function_main(self, latitude, longitude, turbine_name_user, turbine_capacity_user, rotor_diameter_user, turbine_efficiency_user):
    if not (isinstance(latitude, (int, float)) and isinstance(longitude, (int, float))):
        raise ValueError("Latitude and longitude must be numeric.")

    lon = longitude
    lat = latitude
    turbine_name = turbine_name_user
    turbine_capacity = turbine_capacity_user
    rotor_diameter = rotor_diameter_user
    turbine_efficiency = turbine_efficiency_user

    # Output CSV location
    wind_speed_file = os.path.join(config.timestamped_folder, f"{turbine_name}_wind_data_saved.csv")

    # Fetch and save wind speed data from Open-Meteo
    download_wind_csv_openmeteo(lat, lon, wind_speed_file)

    # Calculate power output
    total_power = calculate_wind_power_with_columns(wind_speed_file, turbine_capacity, turbine_efficiency, rotor_diameter)

    return total_power


def download_wind_csv_openmeteo(lat, lon, wind_speed_file):
    """
    Fetch hourly wind speed data at 100m from Open-Meteo and save as formatted CSV.
    """
    url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "hourly": "wind_speed_120m",
        "wind_speed_unit": "ms"
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    hourly = response.Hourly()
    wind_speeds = hourly.Variables(0).ValuesAsNumpy()
    timestamps = pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )

    df = pd.DataFrame({
        "datetime": timestamps,
        "wind_speed_100m": wind_speeds
    })

    # Extract required date/time columns
    df["Year"] = df["datetime"].dt.year
    df["Month"] = df["datetime"].dt.month
    df["Day"] = df["datetime"].dt.day
    df["Hour"] = df["datetime"].dt.hour
    df["Minute"] = df["datetime"].dt.minute

    # Reorder and rename columns
    df_final = df[["Year", "Month", "Day", "Hour", "Minute", "wind_speed_100m"]]
    df_final.rename(columns={"wind_speed_100m": "Wind Speed at 100m (m/s)"}, inplace=True)

    # Save to CSV
    df_final.to_csv(wind_speed_file, index=False)
    print(f"Wind data saved to {wind_speed_file}")


def calculate_wind_power_with_columns(wind_speed_file, turbine_capacity, turbine_efficiency, rotor_diameter):
    """
    Reads wind speed data from a CSV file, calculates power output, and adds a column for power output.
    """
    try:
        df = pd.read_csv(wind_speed_file)

        required_columns = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'Wind Speed at 100m (m/s)']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"The column '{col}' is missing from the data.")

        df['wind_speed'] = pd.to_numeric(df['Wind Speed at 100m (m/s)'], errors='coerce')

        air_density = 1.225  # kg/m^3
        swept_area = np.pi * (rotor_diameter / 2) ** 2  # m^2

        df['power_output'] = np.minimum(
            0.5 * air_density * swept_area * (df['wind_speed'] ** 3) * (turbine_efficiency / 1000),
            turbine_capacity
        )

        df.to_csv(wind_speed_file, index=False)

        total_power_kwh = df['power_output'].sum()
        print(f"Total wind power produced: {total_power_kwh:.2f} kWh")
        return total_power_kwh

    except Exception as e:
        print(f"An error occurred while calculating wind power: {e}")
