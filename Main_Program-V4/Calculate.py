import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests
import Wind_csv_save
import Solar_PV_csv_save
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import gurobi_multi_objective
import config
import gurobi_multi_objective 
from config import dictionary_transfer
#from Inputs import InputPage

# Example Data for Output Display
# This is just example data. In a real application, this would be replaced with actual data from calculations.
""""
configurations = [
    {'solar': 5, 'solar_panels': 20, 'wind': 10, 'wind_turbines': 4, 'battery': 20, 'battery_units': 10, 'inverter': 5, 'inverters': 1, 'price': 10000},
    {'solar': 8, 'solar_panels': 32, 'wind': 12, 'wind_turbines': 5, 'battery': 25, 'battery_units': 12, 'inverter': 7, 'inverters': 1, 'price': 15000},
    {'solar': 10, 'solar_panels': 40, 'wind': 15, 'wind_turbines': 6, 'battery': 30, 'battery_units': 15, 'inverter': 10, 'inverters': 2, 'price': 20000},
    {'solar': 12, 'solar_panels': 48, 'wind': 18, 'wind_turbines': 7, 'battery': 35, 'battery_units': 18, 'inverter': 12, 'inverters': 2, 'price': 25000}
]
"""
 # This will be the configurations from gurobi_multi_objective



class Calculate_Button(tk.Frame):
    def __init__(self, parent,location_page):
        super().__init__(parent)
        self.parent = parent
        self.location_page =  location_page
      #  self.location.create_location_section(parent)
    
    def gather_input_data(self):
        """Retrieve user input data"""
        
        #Declare Global Variables
       # global city, state, country

        city = self.location_page.city_entry.get()
        state = self.location_page.state_entry.get()
        country = self.location_page.country_entry.get()

        return city, state, country

    def get_coordinates(self, city, state, country):
        """Retrieve coordinates for the given city, state, and country."""
        # LocationIQ API key (insert your API key here)
        self.api_key = "pk.06116c260378fbaf82bb1d519c2e0e2d"
        self.base_url = "https://us1.locationiq.com/v1/search.php"

        location_str = f"{city}, {state}, {country}"

        params = {
            'key': self.api_key,
            'q': location_str,
            'format': 'json'
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Raise an error for bad responses

            data = response.json()
            if data:
                # Get the latitude and longitude from the response
                latitude = data[0]['lat']
                longitude = data[0]['lon']
                return float(latitude),float(longitude)
            else:
                return None, None
        except requests.exceptions.RequestException as e:
            return None, None
        
    def calculate(self):
        """Perform calculations, print results, and open results window."""
        # Prompt the user for the project name
        self.prompt_project_name()
        print(config.load_demand)

    def prompt_project_name(self):
        """Prompt the user for the project name."""
        self.project_name_window = tk.Toplevel(self.parent)
        self.project_name_window.title("Enter Project Name")

        tk.Label(self.project_name_window, text="Project Name:").pack(pady=10)
        self.project_name_entry = tk.Entry(self.project_name_window)
        self.project_name_entry.pack(pady=10)

        tk.Button(self.project_name_window, text="OK", command=self.save_project_name).pack(pady=10)

        self.center_window(self.project_name_window)
        
    def center_window(self, window):
        """Center the given window on the screen."""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def save_project_name(self):
        """Save the project name and proceed with calculations."""
        project_name = self.project_name_entry.get()
        if not project_name:
            config.project_name = "Default_Project"
            messagebox.showwarning("Warning", "Project name is empty. Using default name.")

        else:
            config.project_name = project_name

        # Close the project name window
        self.project_name_window.destroy()

        # Proceed with the calculations
        self.perform_calculations()

    def perform_calculations(self):
        """Perform calculations, print results, and open results window."""

        city, state, country = self.gather_input_data()

        if not city or not state or not country:
            self.open_results_window("Error", "Please enter a valid city, state, and country.")
            return

        latitude, longitude = self.get_coordinates(city, state, country)

        if latitude is not None and longitude is not None:
            try:
                print("pulling wind data")
                for i in config.wind_data_dict:
                    print(f"Processing wind data for configuration {i}: {config.wind_data_dict[i]}")
                    turbine_name_user = str(config.wind_data_dict[i][0])
                    turbine_capacity_user = int(config.wind_data_dict[i][1])
                    rotor_diameter_user = int(config.wind_data_dict[i][4])  # meters
                    turbine_efficiency_user = float(config.wind_data_dict[i][5])  # percentage

                    Wind_csv_save.wind_function_main(
                        self,
                        latitude,
                        longitude,
                        turbine_name_user,
                        turbine_capacity_user,
                        rotor_diameter_user,
                        turbine_efficiency_user
                    )  

                print("pulling solar data")
                
                
                for i in config.pv_data_dict:
                    print(f"Processing solar data for configuration {i}: {config.pv_data_dict[i]}")
                    pv_system_name_user = str(config.pv_data_dict[i][0])
                    pv_capacity_user = int(config.pv_data_dict[i][1])
                    pv_module_type_user = str(config.pv_data_dict[i][4])  
                    
                    try:
                        Solar_PV_csv_save.solar_function(
                            self,
                            latitude,
                            longitude,
                            pv_system_name_user,
                            pv_capacity_user, 
                            pv_module_type_user
                        )
                    except ValueError as e:
                        self.open_results_window(f"Error: {e}")

                
                gurobi_multi_objective.optimization(self)
                configurations = config.dictionary_transfer
                self.open_results_window(configurations)
            except ValueError as e:
                self.open_results_window(f"Error: {e}")
        
        else:
            self.open_results_window("Error", "Could not retrieve coordinates.")
    print("Calculations completed.")


    '''
    def open_results_window(self, message):
        """Open a new window to display the calculation results."""
        results_window = tk.Toplevel(self.master)
        results_window.title("Calculation Results")

        results_frame = ttk.Frame(results_window)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(results_frame, text="Calculation Results", font=('Helvetica', 16)).pack(pady=10)

        # Display latitude and longitude
        tk.Label(results_frame, text=message).pack(anchor='w')
    '''

    def open_results_window(self, configurations):
        """Open a new window to display the calculation results."""
        results_window = tk.Toplevel(self.master)
        results_window.title("Calculation Results")

        # Create main frame
        main_frame = ttk.Frame(results_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left section (Configuration details)
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(left_frame)
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Right section (Charts)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title for the results section
        tk.Label(scrollable_frame, text="Calculation Results", font=('Helvetica', 16)).pack(pady=10)

        total_energies = []
        total_prices = []
        labels = []
        solar_panels = []
        wind_turbines = []
        battery_units = []
        inverters = []
        colors = ['blue', 'green', 'red', 'purple', 'orange', 'cyan']
        component_colors = {
                            "Solar Panels": "#FFD700",  # Yellow
                            "Wind Turbines": "#E3E3E1",  # Pink
                            "Battery Units": "#FA8D7D",  # Red
                            "Inverters": "#DFFA7D"  # Purple
                            }

        # Display configurations (LEFT SECTION)
        for i, config in enumerate(configurations, start=1):
            config_frame = ttk.Frame(scrollable_frame)
            config_frame.pack(fill=tk.BOTH, expand=True, pady=10)

            tk.Label(config_frame, text=f"Configuration {i}", font=('Helvetica', 14, 'bold')).pack(anchor='w')
            tk.Label(config_frame, text=f"Solar: {config['solar']} kW ({config['solar_panels']} panels)").pack(anchor='w')
            tk.Label(config_frame, text=f"Wind: {config['wind']} kW ({config['wind_turbines']} turbines)").pack(anchor='w')
            #tk.Label(config_frame, text=f"Battery: {config['battery']} kWh ({config['battery_units']} units)").pack(anchor='w')
            #tk.Label(config_frame, text=f"Inverter: {config['inverter']} kW ({config['inverters']} units)").pack(anchor='w')
            tk.Label(config_frame, text=f"Price: ${config['price']}").pack(anchor='w')

            #total_energy = config['solar'] + config['wind'] + config['battery']
            #total_energies.append(total_energy)
            #total_prices.append(config['price'])
            labels.append(f"Config {i}")
            
            solar_panels.append(config['solar_panels'])
            wind_turbines.append(config['wind_turbines'])
            #battery_units.append(config['battery_units'])
            #inverters.append(config['inverters'])

        # Create a single figure with 2x2 subplots (RIGHT SECTION)
        fig, ax = plt.subplots(2, 2, figsize=(7, 5))
        
        # Subplot 1: Total Energy per Configuration
        ax[0, 0].bar(labels, total_energies, color=colors[:len(labels)])
        ax[0, 0].set_ylabel("Total Energy (kW+kWh)")
        ax[0, 0].set_title("Total Energy per Configuration")

        # Subplot 2: Total Cost per Configuration
        ax[0, 1].bar(labels, total_prices, color=colors[:len(labels)])
        ax[0, 1].set_ylabel("Total Cost ($)")
        ax[0, 1].set_title("Total Cost per Configuration")

        # Subplot 3: Component Count per Configuration
        width = 0.2
        x = range(len(labels))

        ax[1, 0].bar([i - width*1.5 for i in x], solar_panels, width=width, 
                    label='Solar Panels', color=component_colors["Solar Panels"])
        ax[1, 0].bar([i - width/2 for i in x], wind_turbines, width=width, 
                    label='Wind Turbines', color=component_colors["Wind Turbines"])
        #ax[1, 0].bar([i + width/2 for i in x], battery_units, width=width, 
                    #label='Battery Units', color=component_colors["Battery Units"])
        #ax[1, 0].bar([i + width*1.5 for i in x], inverters, width=width, 
                    #label='Inverters', color=component_colors["Inverters"])

        ax[1, 0].set_xticks(x)
        ax[1, 0].set_xticklabels(labels)
        ax[1, 0].set_ylabel("Component Count")
        ax[1, 0].set_title("Component Count per Configuration")
        ax[1, 0].legend()

        # Subplot 4: Solar vs. Wind Power Comparison
        ax[1, 1].bar(labels, [config['solar'] for config in configurations], label="Solar Power", color='gold')
        ax[1, 1].bar(labels, [config['wind'] for config in configurations], label="Wind Power", color='skyblue', alpha=0.7)
        ax[1, 1].set_ylabel("Power (kW)")
        ax[1, 1].set_title("Solar vs. Wind Power")
        ax[1, 1].legend()

        fig.tight_layout()

        # Create the chart canvas and add it to the RIGHT SECTION
        chart_canvas = FigureCanvasTkAgg(fig, master=right_frame)
        chart_widget = chart_canvas.get_tk_widget()
        chart_widget.pack(expand=True, fill="both")
        chart_canvas.draw()