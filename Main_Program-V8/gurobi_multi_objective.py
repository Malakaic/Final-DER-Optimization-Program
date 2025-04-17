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

    # DER Maximums
    turbine_max = 100
    PV_max = 2000

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

    # Initialize total renewable power production
    total_renewable_power_production = 0  # Declare total renewable power production

    # Ensure only one type of PV and one type of wind turbine is selected
    model.addConstr(gp.quicksum(selected_turbine_type[j] for j in range(len(PowerTurbine))) == 1, "OneTurbineType")
    model.addConstr(gp.quicksum(selected_pv_type[j] for j in range(len(PowerPV))) == 1, "OnePVType")

    # Ensure the number of selected PVs and turbines does not exceed the maximum values
    model.addConstr(num_turbines <= turbine_max, "MaxTurbines")
    model.addConstr(num_pvs <= PV_max, "MaxPVs")

    # Constraints
    for i, row in power_data.iterrows():
        # Calculate available wind power
        current_month = int(row["Month"]) - 1
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

    # Optimize the model before trying to access .X values
    #model.optimize()


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
        for i, row in power_data.iterrows():
            result_row = [
                k + 1,
                row["Month"],
                row["Day"],
                row["Hour"]
            ]

            for idx in range(len(solar_files)):
                result_row.append(row.get(f"PV-{idx+1} Solar Power", 0))

            for idx in range(len(wind_files)):
                result_row.append(row.get(f"Turbine-{idx+1} Power", 0))

            current_month = int(row["Month"]) - 1
            load_value = load_demand[current_month]
            result_row.append(load_value)

            actual_pv_power = sum(
                selected_pv_type[j].X * num_pvs.X * row.get(f"PV-{j+1} Solar Power", 0)
                for j in range(len(PowerPV))
            )
            actual_wind_power = sum(
                selected_turbine_type[j].X * num_turbines.X * row.get(f"Turbine-{j+1} Power", 0)
                for j in range(len(PowerTurbine))
            )
            grid_usage = grid_energy[i].X

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

            configuration_results.append(result_row)

        all_configurations_results.extend(configuration_results)

        
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

        # Save results to dictionary
        configuration_dict = {
            'solar': [selected_pv_type[j].X for j in range(len(PowerPV))],
            'solar_panels': num_pvs.X,
            'wind': [selected_turbine_type[j].X for j in range(len(PowerTurbine))],
            'wind_turbines': num_turbines.X,
            'price': total_cost.getValue()
        }
        previous_solutions.append(configuration_dict)
    print("\n📦 Configurations summary dictionary:")
    for idx, config_entry in enumerate(previous_solutions):
        print(f"Config {idx+1}: {config_entry}")


    global dictionary_transfer
    # Store the selected PV and turbine values, number of PVs and turbines, and total cost in the dictionary    
    config.dictionary_transfer = previous_solutions
    
    flat_results = all_configurations_results

    columns = ["Solution Number", "Month", "Day", "Hour"]
    columns.extend([f"Original-PV-{idx+1} Solar Power" for idx in range(len(solar_files))])
    columns.extend([f"Original-Turbine-{idx+1} Power" for idx in range(len(wind_files))])
    columns.append("Load Value")
    columns.extend(["Actual-PV-Power", "Actual-Wind-Turbine-Power", "Grid-Consumption",
                    "Optimized-PV-Hourly-Cost", "Optimized-Turbine-Hourly-Cost", "Hourly-Grid-Cost"])



    output_df = pd.DataFrame(flat_results, columns=columns)

    unique_configs = output_df["Solution Number"].nunique()
    print(f"\n📝 Number of unique configurations saved: {unique_configs}")

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


    print(f"\n✅ Optimization results for all configurations saved to: {output_excel_path}")
    print("Configurations saved:", output_df["Solution Number"].unique())

"""
    global dictionary_transfer
    # Store the selected PV and turbine values, number of PVs and turbines, and total cost in the dictionary
    config.dictionary_transfer = [{
            'solar': selected_pv_values, 'solar_panels': num_pvs.x, 'wind': selected_turbine_values, 'wind_turbines': num_turbines.x, 'price': total_cost.getValue()

        }
    ]
    
    print(f"Total yearly PV energy generated (actual): {total_yearly_pv_energy}")
    print(f"Total yearly wind energy generated (actual): {total_yearly_wind_energy}")
   """