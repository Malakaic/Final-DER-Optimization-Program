# config.py
#This is where all global variables will be stored, access these variables by importing this file at the top of your code, and using config.(variable_name) to access the variable.

 # Initialize PV-related variables
pv_counter = 1  # Start from 1 or 0 based on your preference

# Dictionary to store PV data (name, capacity, lifespan, efficiency, module type, cost)
pv_data_dict = {}

pv_lifespan = 15  # Lifespan of PV modules in years
wind_counter = 1  # Start from 1 or 0 based on your preference
# Dictionary to store Wind data (name, capacity, lifespan, efficiency, hub height, rotor diameter, cost)
wind_data_dict = {}

wind_lifespan = 20  # Lifespan of wind turbines in years

battery_data_dict = {}  # Dictionary to store Battery data

# Initialize an empty list to store configurations
#project_name = "MILP"  # Default project name

# load demand array (jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec)
load_demand = []  # List to store load demand data
grid_rate = 0.0  # Default grid rate



financial_weight = 25
efficiency_weight = 25
sustainability_weight = 25
power_quality_weight = 25