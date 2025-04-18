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
import datetime
import pandas as pd
#from Inputs import InputPage

# Example usage
configurations = [
    {'solar': 5, 'solar_panels': 20, 'wind': 10, 'wind_turbines': 4, 'battery': 20, 'battery_units': 10, 'inverter': 5, 'inverters': 1, 'price': 10000},
    {'solar': 8, 'solar_panels': 32, 'wind': 12, 'wind_turbines': 5, 'battery': 25, 'battery_units': 12, 'inverter': 7, 'inverters': 1, 'price': 15000},
    {'solar': 10, 'solar_panels': 40, 'wind': 15, 'wind_turbines': 6, 'battery': 30, 'battery_units': 15, 'inverter': 10, 'inverters': 2, 'price': 20000},
    {'solar': 12, 'solar_panels': 48, 'wind': 18, 'wind_turbines': 7, 'battery': 35, 'battery_units': 18, 'inverter': 12, 'inverters': 2, 'price': 25000}
]

class Calculate_Button(tk.Frame):
    def __init__(self, parent,location_page):
        super().__init__(parent)
        self.parent = parent
        self.location_page =  location_page
      #  self.location.create_location_section(parent)
    
    def gather_input_data(self):
        """Retrieve user input data based on the selected mode."""
        input_mode = self.location_page.input_mode.get()  # Get the selected input mode

        if input_mode == "address":
            # Retrieve city, state, and country
            city = self.location_page.city_entry.get().strip()
            state = self.location_page.state_entry.get().strip()
            country = self.location_page.country_entry.get().strip()
            return city, state, country, None, None  # Return None for latitude and longitude
        elif input_mode == "coordinates":
            # Retrieve latitude and longitude
            try:
                latitude = float(self.location_page.latitude_entry.get().strip())
                longitude = float(self.location_page.longitude_entry.get().strip())
                return None, None, None, latitude, longitude  # Return None for city, state, and country
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values for latitude and longitude.")
                return None, None, None, None, None

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
        print("Saving project name...")
        project_name = self.project_name_entry.get()
        if not project_name:
            # Use the default project name if no name is provided
            config.project_name = "Default_Project"
            messagebox.showwarning("Warning", "Project name is empty. Using default name.")
        else:
            config.project_name = project_name
       
        # Create the project folder path
        project_folder = os.path.join(os.getcwd(), config.project_name)

        # Generate a timestamped folder name
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        timestamped_folder = os.path.join(project_folder, timestamp)

        # Create the timestamped folder
        os.makedirs(timestamped_folder, exist_ok=True)

        # Update the config with the timestamped folder path
        config.timestamped_folder = timestamped_folder

        # Close the project name window
        self.project_name_window.destroy()

        # Proceed with the calculations
        self.perform_calculations()

    def perform_calculations(self):

        city, state, country, latitude, longitude = self.gather_input_data()

        if city and state and country:
                # Address mode: Get coordinates from the address
                latitude, longitude = self.get_coordinates(city, state, country)
                if latitude is None or longitude is None:
                    self.open_results_window("Error", "Could not retrieve coordinates for the given address.")
                    return
        elif latitude is not None and longitude is not None:
                # Coordinates mode: Use the provided latitude and longitude
                pass
        else:
                # Invalid input
                self.open_results_window("Error", "Please provide valid location inputs.")
                return

        
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
    def save_graph(self, fig):
        """Save the graph as an image file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if file_path:
            fig.savefig(file_path)
            messagebox.showinfo("Save Graph", f"Graph saved successfully at {file_path}")


    def open_results_window(self, configurations):

        """Open a new window to display the calculation results."""
        results_window = tk.Toplevel(self.master)
        results_window.title("Calculation Results")

        # Create main frame
        main_frame = ttk.Frame(results_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left section (Optimal Configuration details)
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Right section (Graph)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title for the results section
        tk.Label(left_frame, text="Optimal Configuration", font=('Helvetica', 16)).pack(pady=10)


        # Extract data from the global dictionary
        # Ensure selected_turbine_type is an iterable
        selected_turbine_type = config.dictionary_transfer.get('selected_turbine_type', [])
        if selected_turbine_type is None:
            selected_turbine_type = []

        # Ensure selected_pv_type is an iterable
        selected_pv_type = config.dictionary_transfer.get('selected_pv_type', [])
        if selected_pv_type is None:
            selected_pv_type = []

        # Extract other values from the dictionary, providing defaults if not found
        num_pvs = config.dictionary_transfer.get('num_pvs', 0)
        num_turbines = config.dictionary_transfer.get('num_turbines', 0)
        pv_lcoe = config.dictionary_transfer.get('pv_lcoe', 0)
        turbine_lcoe = config.dictionary_transfer.get('turbine_lcoe', 0)
        grid_lcoe = config.dictionary_transfer.get('grid_lcoe', 0)
        total_lcoe = config.dictionary_transfer.get('total_lcoe', 0)
        total_yearly_cost = config.dictionary_transfer.get('total_yearly_cost', 0)
        total_yearly_pv_energy = config.dictionary_transfer.get('total_yearly_pv_energy', 0)
        total_yearly_wind_energy = config.dictionary_transfer.get('total_yearly_wind_energy', 0)
        total_grid_energy = config.dictionary_transfer.get('total_grid_energy', 0)
        total_renewable_power_production = config.dictionary_transfer.get('total_renewable_power_production', 0)
        turbine_installation_cost = config.dictionary_transfer.get('turbine_installation_cost', 0)
        pv_installation_cost = config.dictionary_transfer.get('pv_installation_cost', 0)

        # Load the output Excel file
        output_excel_path = os.path.join(config.timestamped_folder, "DER_Optimization_Results_Final_Version.xlsx")
        output_df = pd.read_excel(output_excel_path)

        # Configuration Section
        config_frame = ttk.Frame(left_frame)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        tk.Label(config_frame, text="Configuration", font=('Helvetica', 14, 'bold')).pack(anchor='w', pady=5)
        tk.Label(config_frame, text=f"Selected PV Type(s): {', '.join(selected_pv_type)}").pack(anchor='w')
        tk.Label(config_frame, text=f"Selected Turbine Type(s): {', '.join(selected_turbine_type)}").pack(anchor='w')
        tk.Label(config_frame, text=f"Number of PVs: {num_pvs}").pack(anchor='w')
        tk.Label(config_frame, text=f"Number of Turbines: {num_turbines}").pack(anchor='w')

        # Cost Section
        cost_frame = ttk.Frame(left_frame)
        cost_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        tk.Label(cost_frame, text="Cost", font=('Helvetica', 14, 'bold')).pack(anchor='w', pady=5)
        tk.Label(cost_frame, text=f"PV LCOE: ${pv_lcoe:.2f}/kWh").pack(anchor='w')
        tk.Label(cost_frame, text=f"Turbine LCOE: ${turbine_lcoe:.2f}/kWh").pack(anchor='w')
        tk.Label(cost_frame, text=f"Grid LCOE: ${grid_lcoe:.2f}/kWh").pack(anchor='w')
        tk.Label(cost_frame, text=f"Total LCOE: ${total_lcoe:.2f}/kWh").pack(anchor='w')
        tk.Label(cost_frame, text=f"Total Yearly Cost: ${total_yearly_cost:.2f}").pack(anchor='w')
        tk.Label(cost_frame, text=f"Turbine Installation Cost: ${turbine_installation_cost:.2f}").pack(anchor='w')
        tk.Label(cost_frame, text=f"PV Installation Cost: ${pv_installation_cost:.2f}").pack(anchor='w')

        # Power Section
        power_frame = ttk.Frame(left_frame)
        power_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        tk.Label(power_frame, text="Power", font=('Helvetica', 14, 'bold')).pack(anchor='w', pady=5)
        tk.Label(power_frame, text=f"Total Yearly PV Energy: {total_yearly_pv_energy:.2f} kWh").pack(anchor='w')
        tk.Label(power_frame, text=f"Total Yearly Wind Energy: {total_yearly_wind_energy:.2f} kWh").pack(anchor='w')
        tk.Label(power_frame, text=f"Total Grid Energy: {total_grid_energy:.2f} kWh").pack(anchor='w')
        tk.Label(power_frame, text=f"Total Renewable Power Production: {total_renewable_power_production:.2f} kWh").pack(anchor='w')

        # Graph dropdown menu
        graphs = {
            "Monthly Average Power Output": lambda parent: self.plot_monthly_average_power(parent, output_df),
            "Monthly Power Distribution Breakdown": lambda parent: self.plot_monthly_energy_breakdown(parent, output_df)
            #"Cost Breakdown": self.plot_cost_breakdown
        }

        # Dropdown menu to select graphs
        selected_graph = tk.StringVar(value="Monthly Average Power Output")
        graph_selector = ttk.Combobox(right_frame, textvariable=selected_graph, values=list(graphs.keys()), state="readonly")
        graph_selector.pack(pady=10)

        # Frame to hold the graph
        graph_frame = ttk.Frame(right_frame)
        graph_frame.pack(expand=True, fill="both")

        def update_graph():
            """Update the graph with the selected configuration."""
            # Clear only the contents of the graph frame
            for widget in graph_frame.winfo_children():
                widget.destroy()

            # Call the selected graph function
            graph_function = graphs[selected_graph.get()]
            graph_function(graph_frame)  # Pass the graph_frame as the parent
        
          # Bind the dropdown menu to update the graph
        graph_selector.bind("<<ComboboxSelected>>", lambda event: update_graph())

        # Display the initial graph
        update_graph()

        # Add a "Save Graph" button
        save_button = tk.Button(right_frame, text="Save Graph", command=lambda: self.save_graph(self.current_fig))
        save_button.pack(pady=10)

    def plot_monthly_average_power(self, parent, output_df):
        # Calculate monthly averages
        monthly_averages = output_df.groupby("Month").mean()

        # Extract monthly data
        months = monthly_averages.index
        pv_power_avg = monthly_averages["Actual-PV-Power"]
        wind_power_avg = monthly_averages["Actual-Wind-Turbine-Power"]
        grid_power_avg = monthly_averages["Grid-Consumption"]

        # Define month labels
        month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        # Plot the data
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(months, pv_power_avg, label="PV Power (kW)", color="gold", marker="o")
        ax.plot(months, wind_power_avg, label="Wind Power (kW)", color="skyblue", marker="o")
        ax.plot(months, grid_power_avg, label="Grid Consumption (kW)", color="red", linestyle="--", marker="o")

        # Customize the graph
        ax.set_title("Monthly Average Power Output")
        ax.set_xlabel("Month")
        ax.set_ylabel("Power (kW)")
        ax.set_xticks(months)
        ax.set_xticklabels([month_labels[int(m) - 1] for m in months])  # Convert numeric months to labels
        # Move the legend outside the graph
        ax.legend(loc="upper left", bbox_to_anchor=(1.05, 1), borderaxespad=0.)
        ax.grid(True)

        # Store current graph to save
        self.current_fig = fig
  
        # Add the graph to the right section
        chart_canvas = FigureCanvasTkAgg(fig, master=parent)
        chart_widget = chart_canvas.get_tk_widget()
        chart_widget.pack(expand=True, fill="both")
        chart_canvas.draw()

    def plot_monthly_energy_breakdown(self, parent, output_df):
        """Plot a bar chart showing the energy breakdown for each month."""
        # Calculate monthly totals
        monthly_totals = output_df.groupby("Month").sum()

        # Extract monthly data
        months = monthly_totals.index
        wind_energy = monthly_totals["Actual-Wind-Turbine-Power"]
        pv_energy = monthly_totals["Actual-PV-Power"]
        grid_energy = monthly_totals["Grid-Consumption"]

        # Define month labels
        month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        # Plot the data
        fig, ax = plt.subplots(figsize=(10, 6))
        bar_width = 0.6

        # Create stacked bar chart
        ax.bar(months, wind_energy, bar_width, label="Wind Energy", color="skyblue")
        ax.bar(months, pv_energy, bar_width, bottom=wind_energy, label="PV Energy", color="gold")
        ax.bar(months, grid_energy, bar_width, bottom=wind_energy + pv_energy, label="Grid Energy", color="red")

        # Customize the chart
        ax.set_title("Monthly Energy Breakdown", fontsize=14)
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Energy (kWh)", fontsize=12)
        ax.set_xticks(months)
        ax.set_xticklabels([month_labels[int(m) - 1] for m in months])  # Convert numeric months to labels
        ax.legend(loc="upper left", bbox_to_anchor=(1.05, 1), borderaxespad=0.)
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        # Store current graph to save
        self.current_fig = fig

        # Add the graph to the parent frame
        chart_canvas = FigureCanvasTkAgg(fig, master=parent)
        chart_widget = chart_canvas.get_tk_widget()
        chart_widget.pack(expand=True, fill="both")
        chart_canvas.draw()

       
