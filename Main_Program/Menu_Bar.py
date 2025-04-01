import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import Load_Inputs
import Location_Input
import config


class MenuBar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
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
        """Save current entries to a CSV file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    # Write location data
                    writer.writerow(["City", self.city_entry.get()])
                    writer.writerow(["State", self.state_entry.get()])
                    writer.writerow(["Country", self.country_entry.get()])

                    # Write load demand data
                    writer.writerow(["Load Choice", self.load_choice.get()])
                    if self.load_choice.get() == "CSV Entry":
                        writer.writerow(["CSV File Path", self.csv_entry.get()])
                    else:
                        for month, entry in self.monthly_entries.items():
                            writer.writerow([month, entry.get()])
                    writer.writerow(["Grid Rate", self.grid_rate_entry.get()])

                    # Write weighted objectives data
                    writer.writerow(["Financial", self.financial_entry.get()])
                    writer.writerow(["Efficiency", self.efficiency_obj_entry.get()])
                    writer.writerow(["Sustainability", self.sustainability_entry.get()])

                    # Write DER entries
                    writer.writerow(["Name", "Type", "Cost", "Capacity", "Efficiency"])
                    for child in self.der_tree.get_children():
                        writer.writerow(self.der_tree.item(child)["values"])

                messagebox.showinfo("Success", "Data saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving file: {e}")

    # open CSV file function
    def open_csv(self):
        """Open a CSV file and load the data into the app."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, mode='r') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        if row[0] == "City":
                            self.city_entry.delete(0, tk.END)
                            self.city_entry.insert(0, row[1])
                        elif row[0] == "State":
                            self.state_entry.delete(0, tk.END)
                            self.state_entry.insert(0, row[1])
                        elif row[0] == "Country":
                            self.country_entry.delete(0, tk.END)
                            self.country_entry.insert(0, row[1])
                        elif row[0] == "Grid Rate":
                            self.grid_rate_entry.delete(0, tk.END)
                            self.grid_rate_entry.insert(0, row[1])
                        elif row[0] == "CSV File Path":
                            self.csv_entry.config(state="normal")
                            self.csv_entry.delete(0, tk.END)
                            self.csv_entry.insert(0, row[1])
                            self.csv_entry.config(state="disabled")
                        elif row[0] in ["Financial", "Efficiency", "Sustainability"]:
                            if row[0] == "Financial":
                                self.financial_entry.delete(0, tk.END)
                                self.financial_entry.insert(0, row[1])
                            elif row[0] == "Efficiency":
                                self.efficiency_obj_entry.delete(0, tk.END)
                                self.efficiency_obj_entry.insert(0, row[1])
                            elif row[0] == "Sustainability":
                                self.sustainability_entry.delete(0, tk.END)
                                self.sustainability_entry.insert(0, row[1])
                        elif row[0] in self.monthly_entries.keys():
                            # Correctly populate the monthly entries
                            self.monthly_entries[row[0]].delete(0, tk.END)
                            self.monthly_entries[row[0]].insert(0, row[1])
                        elif row[0] == "Name":
                            continue  # Skip the header for DER
                        else:
                            self.der_tree.insert("", "end", values=row)

                messagebox.showinfo("Success", "Data loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error opening file: {e}")

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


