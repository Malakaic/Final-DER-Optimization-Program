import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import Load_Inputs
import Location_Input
import config


class MenuBar(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        
        self.app = app
        self.create_menu()

    def create_menu(self):
        """Creates the menu bar for file operations."""
        menu_bar = tk.Menu(self.master)

        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Save as CSV", command=self.save_to_csv)
        file_menu.add_command(label="Open CSV", command=self.open_csv)
        file_menu.add_command(label="Clear All", command=self.clear_all)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # View menu
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Saved PVs", command=self.view_saved_pvs)
        view_menu.add_command(label="Saved Turbines", command=self.view_saved_turbines)
        view_menu.add_command(label="Saved Batteries", command=self.view_saved_batteries)
        view_menu.add_command(label="Saved Inverters", command=self.view_saved_inverters)
        menu_bar.add_cascade(label="View", menu=view_menu)

        self.master.config(menu=menu_bar)

    def view_saved_pvs(self):
        """Handle View Saved PVs."""
        pv_window = tk.Toplevel()
        pv_window.title("Saved PVs")

        labels = ["Name", "Size (kW-DC)", "Cost ($/kW-DC)", "Lifespan (years)", "Module Type", "Efficiency (%)"]
        for i, label in enumerate(labels):
            tk.Label(pv_window, text=label).grid(row=0, column=i)

        # Assuming config.pv_data_dict is a dictionary where values are lists of PV attributes
        for row_index, (key, row_data) in enumerate(config.pv_data_dict.items(), start=1):
            for col_index, item in enumerate(row_data):
                tk.Label(pv_window, text=item).grid(row=row_index, column=col_index)


    def view_saved_turbines(self):
        """Handle View Saved Turbines."""
        turbine_window = tk.Toplevel()
        turbine_window.title("Saved Turbines")

        labels = ["Name", "Size (kW AC)", "Hub Height (meters)", "Lifespan (years)", "Rotor Diameter (meters)", "Efficiency (%)"]
        for i, label in enumerate(labels):
            tk.Label(turbine_window, text=label).grid(row=0, column=i)

        # Assuming config.wind_data_dict is a dictionary where values are lists of turbine attributes
        for row_index, (key, row_data) in enumerate(config.wind_data_dict.items(), start=1):
            for col_index, item in enumerate(row_data):
                tk.Label(turbine_window, text=item).grid(row=row_index, column=col_index)

    def view_saved_batteries(self):
        """Handle View Saved Batteries."""
        battery_window = tk.Toplevel()
        battery_window.title("Saved Batteries")

        labels = ["Name", "Energy capacity cost ($/kWh)", "Power capacity cost ($/kW)", "Allow grid to charge battery", "Minimum energy capacity (kWh)", "Maximum energy capacity (kWh)"]
        for i, label in enumerate(labels):
            tk.Label(battery_window, text=label).grid(row=0, column=i)

        # Assuming config.battery_data_dict is a dictionary where values are lists of battery attributes
        for row_index, (key, row_data) in enumerate(config.battery_data_dict.items(), start=1):
            for col_index, item in enumerate(row_data):
                tk.Label(battery_window, text=item).grid(row=row_index, column=col_index)

    def view_saved_inverters(self):
        """Handle View Saved Inverters."""
        messagebox.showinfo("Saved Inverters", "Saved Inverters selected")

    # Save to CSV file function
    def save_to_csv(self):
        
        """Save all GUI data to a CSV file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return  # User canceled the save dialog

        # Collect data from GUI fields
        data = {
            "location": self.location_page.get_data(),  # Assuming `get_data` returns a dictionary of location data
            "load_demand": self.load_page.get_data(),  # Assuming `get_data` returns a dictionary of load demand data
            "objectives": self.objective_page.get_data(),  # Assuming `get_data` returns a dictionary of objectives
            "der": self.der_page.get_data()  # Assuming `get_data` returns a dictionary of DER data
        }

        # Write data to CSV
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            for section, section_data in data.items():
                writer.writerow([section])  # Write section name
                for key, value in section_data.items():
                    writer.writerow([key, value])  # Write key-value pairs
                writer.writerow([])  # Blank line between sections

        messagebox.showinfo("Save Data", "Data saved successfully!")

    # open CSV file function
    def open_csv(self):
        """Load GUI data from a CSV file."""
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return  # User canceled the open dialog

        # Read data from CSV
        data = {}
        current_section = None
        with open(file_path, mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                if not row:
                    continue  # Skip blank lines
                if len(row) == 1:  # Section name
                    current_section = row[0]
                    data[current_section] = {}
                elif current_section and len(row) == 2:  # Key-value pair
                    key, value = row
                    data[current_section][key] = value

        # Populate GUI fields with loaded data
        self.location_page.set_data(data.get("location", {}))  # Assuming `set_data` populates location fields
        self.load_page.set_data(data.get("load_demand", {}))  # Assuming `set_data` populates load demand fields
        self.objective_page.set_data(data.get("objectives", {}))  # Assuming `set_data` populates objectives
        self.der_page.set_data(data.get("der", {}))  # Assuming `set_data` populates DER fields

        messagebox.showinfo("Load Data", "Data loaded successfully!")

    def clear_all(self):
        """Clear all input fields."""
        self.city_entry.delete(0, tk.END)
        self.state_entry.delete(0, tk.END)
        self.country_entry.delete(0, tk.END)
        self.grid_rate_entry.delete(0, tk.END)
        self.csv_entry.delete(0, tk.END)
        self.financial_entry.delete(0, tk.END)
        self.efficiency_obj_entry.delete(0, tk.END)
        self.sustainability_entry.delete(0, tk.END)
        for entry in self.monthly_entries.values():
            entry.delete(0, tk.END)
        self.der_tree.delete(*self.der_tree.get_children())


