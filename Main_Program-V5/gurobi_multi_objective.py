import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import config
import os
import datetime

def optimization(self):
    # Parameters
    load_demand = config.load_demand # Total hourly load demand (kW)
    PowerTurbine = [config.wind_data_dict[i][1] for i in config.wind_data_dict]  # Wind turbine capacities (kW)
    PowerPV = [config.pv_data_dict[i][1] for i in config.pv_data_dict]  # Solar PV capacities (kW)

    # Cost per kWh for DER components
    costTurbine = [int(config.wind_data_dict[i][6]) for i in config.wind_data_dict]  # Wind turbine costs
    costPV = [int(config.pv_data_dict[i][5]) for i in config.pv_data_dict]  # Solar PV costs
    costgrid = config.grid_rate  # Grid energy cost per kWh

    # Lifespan in hours (24 hours * 365 days * 10 years)
    turbine_lifespan_hours = 24 * 365 * config.wind_lifespan
    pv_lifespan_hours = 24 * 365 * config.pv_lifespan


    timestamped_folder = config.timestamped_folder

    print(f"PV Configurations: {config.pv_data_dict}")
    print(f"Wind Configurations: {config.wind_data_dict}")


    solar_files = [f for f in os.listdir(timestamped_folder) if f.endswith("_solar_data_saved.csv")]
    solar_dfs = []
    for idx, file in enumerate(solar_files):
        file_path = os.path.join(timestamped_folder, file)
        df = pd.read_csv(file_path, skiprows=28, usecols=[0, 1, 2, 3], names=["Month", "Day", "Hour", f"PV-{idx+1} Solar Power"], header=0)
        df[f"PV-{idx+1} Solar Power"] /= 1000
        solar_dfs.append(df)

    # Merge solar data on Month, Day, Hour
    solar_df = solar_dfs[0] if solar_dfs else pd.DataFrame(columns=["Month", "Day", "Hour"])
    for df in solar_dfs[1:]:
        solar_df = pd.merge(solar_df, df, on=["Month", "Day", "Hour"], how="outer")

    # Load Wind Power Data
    wind_files = [f for f in os.listdir(timestamped_folder) if f.endswith("_wind_data_saved.csv")]
    wind_dfs = []
    for idx, file in enumerate(wind_files):
        file_path = os.path.join(timestamped_folder, file)
        df = pd.read_csv(file_path, usecols=[1, 2, 3, 7], names=["Month", "Day", "Hour", f"Turbine-{idx+1} Power"], header=0)
        wind_dfs.append(df)

    # Merge wind data on Month, Day, Hour
    wind_df = wind_dfs[0] if wind_dfs else pd.DataFrame(columns=["Month", "Day", "Hour"])
    for df in wind_dfs[1:]:
        wind_df = pd.merge(wind_df, df, on=["Month", "Day", "Hour"], how="outer")


    # Convert month names to numbers if necessary
    month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
    if solar_df["Month"].dtype == object:
        solar_df["Month"] = solar_df["Month"].map(month_map)
    if wind_df["Month"].dtype == object:
        wind_df["Month"] = wind_df["Month"].map(month_map)

    # Ensure consistent data types
    solar_df[["Month", "Day", "Hour"]] = solar_df[["Month", "Day", "Hour"]].astype(int)
    wind_df[["Month", "Day", "Hour"]] = wind_df[["Month", "Day", "Hour"]].astype(int)

    # Merge data
    # Merge solar and wind data on Month, Day, Hour
    power_data = pd.merge(solar_df, wind_df, on=["Month", "Day", "Hour"], how="outer")

    # Save combined CSV
    combined_csv_path = os.path.join(timestamped_folder, "Combined_Power_Data.csv")
    power_data.to_csv(combined_csv_path, index=False)

    # Calculate the highest possible installation cost
    pv_costs = [data[5] for data in config.pv_data_dict.values()]
    turbine_costs = [data[6] for data in config.wind_data_dict.values()]

    pv_capacities = [data[1] for data in config.pv_data_dict.values()]
    turbine_capacities = [data[1] for data in config.wind_data_dict.values()]


    # Initialize model
    model = gp.Model("DER_Optimization")

    # Decision variables
    selected_turbine_type = model.addVars(len(PowerTurbine), vtype=GRB.BINARY, name="SelectedTurbineType")
    selected_pv_type = model.addVars(len(PowerPV), vtype=GRB.BINARY, name="SelectedPVType")
    num_turbines = model.addVar(vtype=GRB.INTEGER, name="NumTurbines")
    num_pvs = model.addVar(vtype=GRB.INTEGER, name="NumPVs")
    grid_energy = model.addVars(len(power_data), vtype=GRB.CONTINUOUS, name="GridEnergy")

    # New variable for actual solar power used
    actual_solar_power_used = model.addVars(len(power_data), vtype=GRB.CONTINUOUS, name="ActualSolarPowerUsed")
    actual_wind_power_used = model.addVars(len(power_data), vtype=GRB.CONTINUOUS, name="ActualWindPowerUsed")

    # Ensure only one type of PV and one type of wind turbine is selected
    model.addConstr(gp.quicksum(selected_turbine_type[j] for j in range(len(PowerTurbine))) == 1, "OneTurbineType")
    model.addConstr(gp.quicksum(selected_pv_type[j] for j in range(len(PowerPV))) == 1, "OnePVType")

    # Ensure the number of selected PVs and turbines does not exceed the maximum values
    model.addConstr(num_turbines <= config.turbine_max, "MaxTurbines")
    model.addConstr(num_pvs <= config.PV_max, "MaxPVs")

    # Constraints
    for i, row in power_data.iterrows():
        # Calculate available wind power
        current_month = int(row["Month"])-1
        current_load_demand = load_demand[current_month]  # Adjust for zero-based index

        model.addConstr(
            actual_wind_power_used[i] <= gp.quicksum(
                selected_turbine_type[j] * num_turbines * row[f"Turbine-{j+1} Power"] for j in range(len(PowerTurbine))
            ),
            name=f"LimitWindPower_{i}"
        )

        # Constraint to limit actual solar power to available solar power
        model.addConstr(
                actual_solar_power_used[i] <= gp.quicksum(
                    selected_pv_type[j] * num_pvs * row[f"PV-{j+1} Solar Power"] for j in range(len(PowerPV))
                ),
                name=f"LimitSolarPower_{i}"
        )
        
        # Load balance constraint considering available wind and actual solar power
        model.addConstr(
            actual_wind_power_used[i] + actual_solar_power_used[i] + grid_energy[i] == current_load_demand,
            name=f"LoadBalance_{i}"
        )

    # Objective function

    # Initialize variables to store the total hourly costs
    total_turbine_hourly_cost = 0
    total_pv_hourly_cost = 0
    total_grid_cost = 0

    # Iterate through each hour in the dataset
    for i, row in power_data.iterrows():
        # Calculate hourly turbine cost for this hour
        turbine_hourly_cost = gp.quicksum(
            selected_turbine_type[j] * num_turbines * costTurbine[j] * row[f"Turbine-{j+1} Power"]
            for j in range(len(PowerTurbine))
        ) / turbine_lifespan_hours

        # Calculate hourly PV cost for this hour
        pv_hourly_cost = gp.quicksum(
            selected_pv_type[j] * num_pvs * costPV[j] * row[f"PV-{j+1} Solar Power"]
            for j in range(len(PowerPV))
        ) / pv_lifespan_hours

        """
        grid_hourly_cost = gp.quicksum(
            grid_energy[j] * costgrid
            for j in range(len(power_data))
        )
        """

        # Add the hourly costs to the totals
        total_turbine_hourly_cost += turbine_hourly_cost
        total_pv_hourly_cost += pv_hourly_cost
        #total_grid_cost += grid_hourly_cost

    # Average the total costs over the length of the dataset
    average_turbine_cost = total_turbine_hourly_cost / len(power_data)
    average_pv_cost = total_pv_hourly_cost / len(power_data)


    # levelized average grid cost
    grid_cost = gp.quicksum(grid_energy[i] * costgrid for i in range(len(power_data)))/len(power_data)

    # total average levelized hourly cost of the system
    total_cost = average_turbine_cost + average_pv_cost + grid_cost


    # Calculate the total energy demand for all time steps
    total_energy_demand = sum(load_demand[int(row["Month"])-1] for _, row in power_data.iterrows())


    #actual_pv_power = sum(selected_pv_type[j] * num_pvs * row.get(f"PV-{j+1} Solar Power", 0) for j in range(len(PowerPV)))
    actual_pv_power = sum(selected_pv_type[j] * num_pvs * row.get(f"PV-{j+1} Solar Power", 0) for j in range(len(PowerPV)))

    actual_wind_power = gp.quicksum(selected_turbine_type[j] * num_turbines * row.get(f"Turbine-{j+1} Power", 0) for j in range(len(PowerTurbine)))
    total_renewable_power_production = gp.quicksum(
        actual_solar_power_used[i] + actual_wind_power_used[i]
        for i in range(len(power_data))
    )

    total_generation = total_renewable_power_production + gp.quicksum(grid_energy[i] for i in range(len(power_data)))



    # Minimum Cost
    model.setObjective(total_cost, GRB.MINIMIZE)
    model.optimize()
    C_min = model.ObjVal

    # Maximum Cost
    model.setObjective(total_cost, GRB.MAXIMIZE)
    model.optimize()
    C_max = model.ObjVal

    # Minimum Renewable Fraction
    model.setObjective(total_renewable_power_production, GRB.MINIMIZE)
    model.optimize()
    R_min = model.ObjVal

    # Maximum Renewable Fraction
    model.setObjective(total_renewable_power_production, GRB.MAXIMIZE)
    model.optimize()
    R_max = model.ObjVal

    def normalize_cost(cost_value):
        return (C_max - cost_value) / (C_max - C_min)

    def normalize_renewable(renewable_value):
        return (renewable_value - R_min) / (R_max - R_min)

    cost_normalized = normalize_cost(total_cost)
    renewable_normalized = normalize_renewable(total_renewable_power_production)

    # Solve model
    model.setObjective(config.cost_weight * cost_normalized + config.renewable_weight * renewable_normalized, GRB.MAXIMIZE)
    model.optimize()

    # Store results
    results = []
    total_grid_energy = 0
    for i, row in power_data.iterrows():
        grid_usage = grid_energy[i].x
        total_grid_energy += grid_usage
        result_row = [
            row["Month"],
            row["Day"],
            row["Hour"]
        ]
        # Add original solar power data
        for idx in range(len(solar_files)):
            result_row.append(row.get(f"PV-{idx+1} Solar Power", 0))
        # Add original wind power data
        for idx in range(len(wind_files)):
            result_row.append(row.get(f"Turbine-{idx+1} Power", 0))
            
        current_month = int(row["Month"]) - 1  # Adjust for zero-based index
        load_value = load_demand[current_month]
        result_row.append(load_value)  # Add the load value to the row

        # Calculate actual power used from selected components
        actual_pv_power = sum(selected_pv_type[j].x * num_pvs.x * row.get(f"PV-{j+1} Solar Power", 0) for j in range(len(PowerPV)))
        actual_wind_power = sum(selected_turbine_type[j].x * num_turbines.x * row.get(f"Turbine-{j+1} Power", 0) for j in range(len(PowerTurbine)))
        # Add actual power used and costs
        result_row.extend([
            actual_pv_power,
            actual_wind_power,
            grid_usage,
            sum(selected_pv_type[j].x * num_pvs.x * costPV[j] * row.get(f"PV-{j+1} Solar Power", 0) for j in range(len(PowerPV))) / pv_lifespan_hours,
            sum(selected_turbine_type[j].x * num_turbines.x * costTurbine[j] * row.get(f"Turbine-{j+1} Power", 0) for j in range(len(PowerTurbine))) / turbine_lifespan_hours,
            grid_usage * costgrid
        ])
        results.append(result_row)

    # Define column names
    columns = ["Month", "Day", "Hour"]
    columns.extend([f"Original-PV-{idx+1} Solar Power" for idx in range(len(solar_files))])
    columns.extend([f"Original-Turbine-{idx+1} Power" for idx in range(len(wind_files))])
    columns.append("Load Value")  # Add the new column for load value
    columns.extend(["Actual-PV-Power", "Actual-Wind-Turbine-Power", "Grid-Consumption", "Optimized-PV-Hourly-Cost", "Optimized-Turbine-Hourly-Cost", "Hourly-Grid-Cost"])

    # Convert results to DataFrame
    output_df = pd.DataFrame(results, columns=columns)

    # Save the output Excel file in the timestamped folder
    output_excel_path = os.path.join(timestamped_folder, "DER_Optimization_Results_Final_Version.xlsx")
    output_df.to_excel(output_excel_path, index=False)

    # Print selected turbine and PV
    
    selected_turbine_idx = [j for j in range(len(PowerTurbine)) if selected_turbine_type[j].x > 0.5]
    selected_pv_idx = [j for j in range(len(PowerPV)) if selected_pv_type[j].x > 0.5]


    print(f"total cost: {total_cost.getValue()}")
    print(f"total renewable power: {total_renewable_power_production.getValue()}")
    print(f"C_min: {C_min}")
    print(f"C_max: {C_max}")
    print(f"R_min: {R_min}")
    print(f"R_max: {R_max}")
    print(f"Normalized Cost: {cost_normalized.getValue()}")
    print(f"Normalized Renewable: {renewable_normalized.getValue()}")

    # Map indices to keys in pv_data_dict
    pv_keys = list(config.pv_data_dict.keys())  # Get the list of keys
    selected_pv_values = [config.pv_data_dict[pv_keys[j]][0] for j in selected_pv_idx]

    # Map indices to keys in wind_data_dict
    wind_keys = list(config.wind_data_dict.keys())  # Get the list of keys
    selected_turbine_values = [config.wind_data_dict[wind_keys[j]][0] for j in selected_turbine_idx]


    print(f"Selected Turbine(s): {selected_turbine_values}")
    print(f"Selected PV(s): {selected_pv_values}")

    # Print the number of each PV and turbine used
    print(f"Number of selected turbines: {num_turbines.x}")
    print(f"Number of selected PVs: {num_pvs.x}")

    # Print installation costs
    print(f"Turbine installation cost: {average_turbine_cost.getValue()}")
    print(f"PV installation cost: {average_pv_cost.getValue()}")


    print(f"Grid yearly cost: {grid_cost.getValue()}")

    # Calculate and print total yearly energy generated from each component using actual data
    total_yearly_pv_energy = sum(
        gp.quicksum(
            selected_pv_type[j].x * num_pvs.x * power_data.at[i, f"PV-{j+1} Solar Power"]
            for j in range(len(PowerPV))
        )
        for i in range(len(power_data))
    )
    total_yearly_wind_energy = sum(
        gp.quicksum(
            selected_turbine_type[j].x * num_turbines.x * power_data.at[i, f"Turbine-{j+1} Power"]
            for j in range(len(PowerTurbine))
        )
        for i in range(len(power_data))
    )


    global dictionary_transfer
    # Store the selected PV and turbine values, number of PVs and turbines, and total cost in the dictionary
    config.dictionary_transfer = [{
            'solar': selected_pv_values, 'solar_panels': num_pvs.x, 'wind': selected_turbine_values, 'wind_turbines': num_turbines.x, 'price': total_cost.getValue()

        }
    ]
    
    print(f"Total yearly PV energy generated (actual): {total_yearly_pv_energy}")
    print(f"Total yearly wind energy generated (actual): {total_yearly_wind_energy}")
   