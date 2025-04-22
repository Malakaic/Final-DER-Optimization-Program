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

        # Toggle between "City, State, Country" and "Latitude, Longitude"
        self.input_mode = tk.StringVar(value="address")  # Default to "address" mode

        mode_frame = ttk.Frame(location_frame)
        mode_frame.grid(row=0, column=0, columnspan=4, pady=5)
        ttk.Radiobutton(mode_frame, text="City, State, Country", variable=self.input_mode, value="address", command=self.update_input_mode).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Latitude, Longitude", variable=self.input_mode, value="coordinates", command=self.update_input_mode).pack(side=tk.LEFT, padx=5)

        # Address input fields
        self.address_frame = ttk.Frame(location_frame)
        self.address_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=5)

        tk.Label(self.address_frame, text="City:").grid(row=0, column=0, padx=5)
        self.city_entry = tk.Entry(self.address_frame)
        self.city_entry.grid(row=0, column=1, padx=5)

        tk.Label(self.address_frame, text="State:").grid(row=0, column=2, padx=5)
        self.state_entry = tk.Entry(self.address_frame)
        self.state_entry.grid(row=0, column=3, padx=5)

        tk.Label(self.address_frame, text="Country:").grid(row=1, column=0, padx=5)
        self.country_entry = tk.Entry(self.address_frame)
        self.country_entry.grid(row=1, column=1, padx=5)

        # Coordinates input fields
        self.coordinates_frame = ttk.Frame(location_frame)
        self.coordinates_frame.grid(row=2, column=0, columnspan=4, sticky="nsew", pady=5)
        self.coordinates_frame.grid_remove()  # Hide by default

        tk.Label(self.coordinates_frame, text="Latitude:").grid(row=0, column=0, padx=5)
        self.latitude_entry = tk.Entry(self.coordinates_frame)
        self.latitude_entry.grid(row=0, column=1, padx=5)

        tk.Label(self.coordinates_frame, text="Longitude:").grid(row=0, column=2, padx=5)
        self.longitude_entry = tk.Entry(self.coordinates_frame)
        self.longitude_entry.grid(row=0, column=3, padx=5)

        # Ensure the frame expands properly
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        location_frame.grid_rowconfigure(0, weight=1)
        location_frame.grid_rowconfigure(1, weight=1)
        location_frame.grid_rowconfigure(2, weight=1)

    def update_input_mode(self):
        """Update the input fields based on the selected mode."""
        if self.input_mode.get() == "address":
            self.address_frame.grid()
            self.coordinates_frame.grid_remove()
        elif self.input_mode.get() == "coordinates":
            self.coordinates_frame.grid()
            self.address_frame.grid_remove()


    def save_location(self):
        
        """Saves the entered location data."""
        if self.input_mode.get() == "address":
            # Address mode: Get city, state, and country
            city = self.city_entry.get()
            state = self.state_entry.get()
            country = self.country_entry.get()

            if not city or not state or not country:
                messagebox.showerror("Error", "Please enter a valid city, state, and country.")
                return

            latitude, longitude = self.get_coordinates(city, state, country)
        elif self.input_mode.get() == "coordinates":
            # Coordinates mode: Get latitude and longitude
            try:
                latitude = float(self.latitude_entry.get())
                longitude = float(self.longitude_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values for latitude and longitude.")
                return

        # Save the coordinates to the config
        config.latitude = latitude
        config.longitude = longitude

        if latitude is None or longitude is None:
            messagebox.showerror("Error", "Unable to retrieve coordinates. Please check your input.")
            return

        print(f"Saved Location: Latitude={config.latitude}, Longitude={config.longitude}")


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
