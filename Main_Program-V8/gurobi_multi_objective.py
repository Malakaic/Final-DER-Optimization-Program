import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import config
import os
import datetime
import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import config
import os
import datetime

def optimization(self):
    # Parameters
    load_demand = config.load_demand  # Total hourly load demand (kW)
    PowerTurbine = [config.wind_data_dict[i][1] for i in config.wind_data_dict]  # Wind turbine capacities (kW)
    PowerPV = [config.pv_data_dict[i][1] for i in config.pv_data_dict]  # Solar PV capacities (kW)

    # Cost per kWh for DER components
    costTurbine = [int(config.wind_data_dict[i][6]) for i in config.wind_data_dict]  # Wind turbine costs
    costPV = [int(config.pv_data_dict[i][5]) for i in config.pv_data_dict]  # Solar PV costs
    costgrid = config.grid_rate  # Grid energy cost per kWh

    # Lifespan in hours (24 hours * 365 days * 10 years)
    turbine_lifespan_hours = [24 * 365 * int(config.wind_data_dict[i][2]) for i in config.wind_data_dict]
    pv_lifespan_hours = [24 * 365 * int(config.pv_data_dict[i][2]) for i in config.pv_data_dict]

<<<<<<< HEAD
    # DER Maximums
    turbine_max = 100
    PV_max = 2000
=======
>>>>>>> 5079750f0e8e7030ab7e9242a726dd167d132f92

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
    power_data = pd.merge(solar_df, wind_df, on=["Month", "Day", "Hour"], how="outer")

    # Save combined CSV
    combined_csv_path = os.path.join(timestamped_folder, "Combined_Power_Data.csv")
    power_data.to_csv(combined_csv_path, index=False)

    # Initialize a list to store the best configurations
    best_configurations = []

<<<<<<< HEAD
    # Decision variables
    selected_turbine_type = model.addVars(len(PowerTurbine), vtype=GRB.BINARY, name="SelectedTurbineType")
    selected_pv_type = model.addVars(len(PowerPV), vtype=GRB.BINARY, name="SelectedPVType")
    num_turbines = model.addVar(vtype=GRB.INTEGER, name="NumTurbines")
    num_pvs = model.addVar(vtype=GRB.INTEGER, name="NumPVs")

    grid_energy = model.addVars(len(power_data), vtype=GRB.CONTINUOUS, name="GridEnergy")
=======
    for iteration in range(5):  # Iterate 5 times
        # Initialize model
        model = gp.Model("DER_Optimization")
>>>>>>> 5079750f0e8e7030ab7e9242a726dd167d132f92

        # Decision variables
        selected_turbine_type = model.addVars(len(PowerTurbine), vtype=GRB.BINARY, name="SelectedTurbineType")
        selected_pv_type = model.addVars(len(PowerPV), vtype=GRB.BINARY, name="SelectedPVType")
        num_turbines = model.addVar(vtype=GRB.INTEGER, name="NumTurbines")
        num_pvs = model.addVar(vtype=GRB.INTEGER, name="NumPVs")
        grid_energy = model.addVars(len(power_data), vtype=GRB.CONTINUOUS, name="GridEnergy")

        # New variable for actual solar and wind power used
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
            current_month = int(row["Month"]) - 1
            current_load_demand = load_demand[current_month]  # Adjust for zero-based index

            model.addConstr(
                actual_wind_power_used[i] <= gp.quicksum(
                    selected_turbine_type[j] * num_turbines * row[f"Turbine-{j+1} Power"] for j in range(len(PowerTurbine))
                ),
                name=f"LimitWindPower_{i}"
            )

            model.addConstr(
                actual_solar_power_used[i] <= gp.quicksum(
                    selected_pv_type[j] * num_pvs * row[f"PV-{j+1} Solar Power"] for j in range(len(PowerPV))
                ),
                name=f"LimitSolarPower_{i}"
            )

            model.addConstr(
                actual_wind_power_used[i] + actual_solar_power_used[i] + grid_energy[i] == current_load_demand,
                name=f"LoadBalance_{i}"
            )

        # Objective function
        total_turbine_hourly_cost = 0
        total_pv_hourly_cost = 0

<<<<<<< HEAD
    # Update the total renewable power production after optimization
    total_renewable_power_production = sum(actual_solar_power_used[i] + actual_wind_power_used[i] for i in range(len(power_data)))

    # Objective function
    total_turbine_hourly_cost = 0
    total_pv_hourly_cost = 0
    total_grid_cost = 0

    # Iterate through each hour in the dataset
    for i, row in power_data.iterrows():
        turbine_hourly_cost = gp.quicksum(
            selected_turbine_type[j] * num_turbines * costTurbine[j] * row[f"Turbine-{j+1} Power"]
            / turbine_lifespan_hours[j]
            for j in range(len(PowerTurbine))
        ) 

        pv_hourly_cost = gp.quicksum(
            selected_pv_type[j] * num_pvs * costPV[j] * row[f"PV-{j+1} Solar Power"]
            / pv_lifespan_hours[j]
            for j in range(len(PowerPV))
        ) 

        total_turbine_hourly_cost += turbine_hourly_cost
        total_pv_hourly_cost += pv_hourly_cost

    average_turbine_cost = total_turbine_hourly_cost / len(power_data)
    average_pv_cost = total_pv_hourly_cost / len(power_data)

    # levelized average grid cost
    grid_cost = gp.quicksum(grid_energy[i] * costgrid for i in range(len(power_data))) / len(power_data)

    # total average levelized hourly cost of the system
    total_cost = average_turbine_cost + average_pv_cost + grid_cost

    # Calculate the total energy demand for all time steps
    total_energy_demand = sum(load_demand[int(row["Month"]) - 1] for _, row in power_data.iterrows())

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

    #normalized_cost = normalize_cost(C_min)
    normalized_cost = normalize_cost(total_cost)
    renewable_normalized = normalize_renewable(total_renewable_power_production)
    model.Params.MIPGap = 0.1

    # Store full results across all configurations
    all_configurations_results = []

    # Track previously selected DER combinations
    previous_solutions = []

    for k in range(4):  # We want 4 distinct configurations
        # Set the final combined objective again
        normalized_cost = normalize_cost(total_cost.getValue())
        renewable_normalized = normalize_renewable(total_renewable_power_production.getValue())
        penalty_expr = num_turbines + num_pvs
        model.setObjective(config.cost_weight * normalized_cost + config.renewable_weight * renewable_normalized, GRB.MAXIMIZE)
        
        model.optimize()
        if model.Status != GRB.OPTIMAL and model.Status != GRB.TIME_LIMIT:
            print(f"Optimization for configuration {k+1} failed or was infeasible.")
            break

        # Extract which turbine and PV types were selected
        turbine_selection = [j for j in range(len(PowerTurbine)) if selected_turbine_type[j].X > 0.5]
        pv_selection = [j for j in range(len(PowerPV)) if selected_pv_type[j].X > 0.5]

        print(f"\nSolution {k+1}:")
        print(f"Selected Turbine Types: {turbine_selection}")
        print(f"Selected PV Types: {pv_selection}")

        # Collect results for each hour
        configuration_results = []
=======
        # Iterate through each hour in the dataset to calculate hourly costs
>>>>>>> 5079750f0e8e7030ab7e9242a726dd167d132f92
        for i, row in power_data.iterrows():
            turbine_hourly_cost = gp.quicksum(
                selected_turbine_type[j] * num_turbines * costTurbine[j] * row[f"Turbine-{j+1} Power"]
                for j in range(len(PowerTurbine))
            ) / turbine_lifespan_hours

<<<<<<< HEAD
            selected_pv_cost = sum(
                selected_pv_type[j].X * num_pvs.X * costPV[j] * row.get(f"PV-{j+1} Solar Power", 0) / pv_lifespan_hours[j]
                for j in range(len(PowerPV))
            )
            selected_turbine_cost = sum(
                selected_turbine_type[j].X * num_turbines.X * costTurbine[j] * row.get(f"Turbine-{j+1} Power", 0) / turbine_lifespan_hours[j]
                for j in range(len(PowerTurbine))
            )

            result_row.extend([
                actual_pv_power,
                actual_wind_power,
                grid_usage,
                selected_pv_cost,
                selected_turbine_cost,
                grid_usage * costgrid
            ])
=======
            pv_hourly_cost = gp.quicksum(
                selected_pv_type[j] * num_pvs * costPV[j] * row[f"PV-{j+1} Solar Power"]
                for j in range(len(PowerPV))
            ) / pv_lifespan_hours
>>>>>>> 5079750f0e8e7030ab7e9242a726dd167d132f92

            total_turbine_hourly_cost += turbine_hourly_cost
            total_pv_hourly_cost += pv_hourly_cost
            # Average the total costs over the length of the dataset
        average_turbine_cost = total_turbine_hourly_cost / len(power_data)
        average_pv_cost = total_pv_hourly_cost / len(power_data)

        # Calculate grid cost
        grid_cost = gp.quicksum(grid_energy[i] * costgrid for i in range(len(power_data))) / len(power_data)

<<<<<<< HEAD
        
        # Exclude current solution from next iterations
        exclusion_expr = gp.quicksum(selected_turbine_type[j] for j in turbine_selection) + \
                        gp.quicksum(selected_pv_type[j] for j in pv_selection)
        model.addConstr(exclusion_expr <= len(turbine_selection) + len(pv_selection) - 1,
                        name=f"Exclude_Solution_{k+1}")
        

                # Extract and print results
        print(f"\n🌀 Configuration {k + 1} Summary:")
        print(f"Selected Turbine(s): {[selected_turbine_type[j].X for j in range(len(PowerTurbine))]}")
        print(f"Selected PV(s): {[selected_pv_type[j].X for j in range(len(PowerPV))]}")
        print(f"Number of selected turbines: {num_turbines.X}")
        print(f"Number of selected PVs: {num_pvs.X}")
        print(f"Turbine installation cost: {average_turbine_cost.getValue():.2f}")
        print(f"PV installation cost: {average_pv_cost.getValue():.2f}")
        print(f"Grid yearly cost: {grid_cost.getValue():.2f}")
=======
        # Total average levelized hourly cost of the system
        total_cost = total_turbine_hourly_cost + total_pv_hourly_cost + grid_cost
>>>>>>> 5079750f0e8e7030ab7e9242a726dd167d132f92

        # Renewable power production
        total_renewable_power_production = gp.quicksum(
            actual_solar_power_used[i] + actual_wind_power_used[i]
            for i in range(len(power_data))
        )

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

        # Set the objective function
        model.setObjective(config.cost_weight * total_cost + config.renewable_weight * total_renewable_power_production, GRB.MAXIMIZE)
        model.optimize()

        # Store results
        total_cost_value = total_cost.getValue()
        total_renewable_power_value = total_renewable_power_production.getValue()

            
        selected_turbine_idx = [j for j in range(len(PowerTurbine)) if selected_turbine_type[j].x > 0.5]
        selected_pv_idx = [j for j in range(len(PowerPV)) if selected_pv_type[j].x > 0.5]


            # Map indices to keys in pv_data_dict
        pv_keys = list(config.pv_data_dict.keys())  # Get the list of keys
        selected_pv_values = [config.pv_data_dict[pv_keys[j]][0] for j in selected_pv_idx]

        # Map indices to keys in wind_data_dict
        wind_keys = list(config.wind_data_dict.keys())  # Get the list of keys
        selected_turbine_values = [config.wind_data_dict[wind_keys[j]][0] for j in selected_turbine_idx]


        current_configuration = {
            'iteration': iteration,
            'total_cost': total_cost_value,
            'total_renewable_power': total_renewable_power_value,
            'selected_turbine_values': selected_turbine_values,
            'selected_pv_values': selected_pv_values,
            'num_turbines': num_turbines.x,
            'num_pvs': num_pvs.x
        }
        best_configurations.append(current_configuration)

        # Adjust weights based on previous results to find the next best configuration
        if iteration > 0:
            previous_cost = best_configurations[iteration - 1]['total_cost']
            previous_renewable = best_configurations[iteration - 1]['total_renewable_power']
            
            # Update the weights based on the previous iteration
            config.cost_weight = max(0, config.cost_weight - 0.05 * (previous_cost - total_cost_value) / previous_cost)
            config.renewable_weight = max(0, config.renewable_weight - 0.05 * (previous_renewable - total_renewable_power_value) / previous_renewable)

    # Sort and store the best configurations
    best_configurations.sort(key=lambda x: x['total_cost'])

    # Store second, third, fourth, and fifth best configurations
    config.second_best = best_configurations[1] if len(best_configurations) > 1 else None
    config.third_best = best_configurations[2] if len(best_configurations) > 2 else None
    config.fourth_best = best_configurations[3] if len(best_configurations) > 3 else None
    config.fifth_best = best_configurations[4] if len(best_configurations) > 4 else None

    # Print the configurations if needed
    for idx, conf in enumerate(best_configurations):
        print(f"Iteration {idx}: Total Cost: {conf['total_cost']}, Total Renewable Power: {conf['total_renewable_power']}")
        print(f"Selected Turbines: {conf['selected_turbine_values']}, Number of Turbines: {conf['num_turbines']}")
        print(f"Selected PVs: {conf['selected_pv_values']}, Number of PVs: {conf['num_pvs']}")
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

    # Save to Excel
    output_df.to_excel("DER_Optimization_Results_Final_Version.xlsx", index=False)

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

<<<<<<< HEAD
    output_excel_path = os.path.join(timestamped_folder, "DER_Optimization_Results_Final_Version.xlsx")


    # Check if output_df is not empty
    if not output_df.empty:
        # Create an Excel writer object
        with pd.ExcelWriter(output_excel_path, engine="openpyxl") as writer:
            # Loop through each unique solution number
            for solution_number in output_df["Solution Number"].unique():
                # Filter the DataFrame for the current solution number
                solution_df = output_df[output_df["Solution Number"] == solution_number]
                
                # Write the filtered DataFrame to a separate sheet
                sheet_name = f"Solution_{int(solution_number)}"
                solution_df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Optionally, write a summary sheet with all configurations
            output_df.to_excel(writer, sheet_name="Summary", index=False)

        print(f"\n✅ Optimization results for all configurations saved to: {output_excel_path}")
    else:
        print("\n⚠️ No data available in output_df to write to Excel.")

=======
>>>>>>> 5079750f0e8e7030ab7e9242a726dd167d132f92

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
   