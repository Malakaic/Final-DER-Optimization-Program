import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests
import config


class Location(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def create_location_section(self, frame):
        """Creates a location section for data inputs."""
        location_frame = ttk.LabelFrame(frame, text="Location")
        location_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        tk.Label(location_frame, text="City:").grid(row=0, column=0, padx=5)
        self.city_entry = tk.Entry(location_frame)
        self.city_entry.grid(row=0, column=1, padx=5)

        tk.Label(location_frame, text="State:").grid(row=0, column=2, padx=5)
        self.state_entry = tk.Entry(location_frame)
        self.state_entry.grid(row=0, column=3, padx=5)

        tk.Label(location_frame, text="Country:").grid(row=1, column=0, padx=5)
        self.country_entry = tk.Entry(location_frame)
        self.country_entry.grid(row=1, column=1, padx=5)

        # Ensure the frame expands properly
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        location_frame.grid_rowconfigure(0, weight=1)
        location_frame.grid_rowconfigure(1, weight=1)
        location_frame.grid_rowconfigure(2, weight=1)

    def save_location(self):
        """Saves the entered location data."""
        city = self.city_entry.get()
        state = self.state_entry.get()
        country = self.country_entry.get()

        if not city or not state or not country:
            messagebox.showerror("Error", "Please enter a valid city, state, and country.")
            return

        latitude, longitude = self.get_coordinates(city, state, country)
        
        config.latitude = latitude
        config.longitude = longitude

        if latitude is None or longitude is None:
            messagebox.showerror("Error", "Unable to retrieve coordinates. Please check your input.")
            return
        print(config.latitude, config.longitude)


    def get_coordinates(self, city, state, country):
        """Retrieve coordinates for the given city, state, and country."""
        api_key = "pk.06116c260378fbaf82bb1d519c2e0e2d"
        base_url = "https://us1.locationiq.com/v1/search.php"

        location_str = f"{city}, {state}, {country}"

        params = {'key': api_key, 'q': location_str, 'format': 'json'}

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()

            data = response.json()
            if data:
                latitude = data[0]['lat']
                longitude = data[0]['lon']
                return float(latitude), float(longitude)
            else:
                return None, None
        except requests.exceptions.RequestException:
            return None, None
