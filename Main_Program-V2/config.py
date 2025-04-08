# config.py
#This is where all global variables will be stored, access these variables by importing this file at the top of your code, and using config.(variable_name) to access the variable.

 # Initialize PV-related variables
# Dictionary to store PV data (name, capacity, lifespan, efficiency, module type, cost)
pv_data_dict = {
    0: ["Pv-1", 150, 20, 21.6, 0, 200], 
    1: ["Pv-2", 200, 22, 22.4, 1, 250],
    2: ["Pv-3", 250, 18, 25.7, 2, 300]
}  # Dictionary to store PV data

pv_lifespan = 15  # Lifespan of PV modules in years

# Dictionary to store Wind data (name, capacity, lifespan, efficiency, hub height, rotor diameter, cost)
wind_data_dict = {
    0: ["Turbine-1", 1500, 20, 55.7, 100, 65, 2000],
    1: ["Turbine-2", 2000, 18, 67.8, 100, 72, 3000],
    2: ["Turbine-3", 3000, 22, 43.5, 100, 71, 4000]
}  # Dictionary to store PV data

pv_counter = 1
wind_counter = 1

wind_lifespan = 20  # Lifespan of wind turbines in years

battery_data_dict = {}  # Dictionary to store Battery data

# Initialize an empty list to store configurations
project_name = "Default_project"  # Default project name

# load demand array (jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec)
# load demand array (jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec)
#load_demand = [1000, 1200, 1300, 1200, 1400, 1500, 1600, 1700, 1500, 1400, 1200, 1100 ]  # List to store load demand data
load_demand = []
grid_rate = 0.1  # Default grid rate



cost_weight = 50
renewable_weight = 50