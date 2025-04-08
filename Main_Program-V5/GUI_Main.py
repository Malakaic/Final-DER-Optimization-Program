import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests
import config
from Menu_Bar import MenuBar
from Objectives import Objective_Menu
from DERs import Der_menu_page
from Calculate import Calculate_Button
from Load_Inputs import LoadDemandSection
from Location_Input import Location
import datetime



class EnergyResourceApp(tk.Tk):
    def __init__(self, master):
        self.master = master
        self.master.title("Energy Resource Optimization")
        print("Initializing Energy Resource App...")

        # Create the main frame
        self.main_frame = ttk.Frame(self.master)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Create the menu bar
        self.menu = MenuBar(master, self)

        # Create the left side frame
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Ensure left frame rows resize properly
        self.left_frame.grid_rowconfigure(0, weight=1)  # Location Section
        self.left_frame.grid_rowconfigure(1, weight=1)  # Load Demand Section

        # Create the right side frame
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Create the location section (row 0)
        self.location_page = Location(self.master)
        self.location_page.create_location_section(self.left_frame)

        # Create the load demand section (row 1)
        self.load_page = LoadDemandSection(self.master)
        self.load_page.create_load_demand_section(self.left_frame)

        # Create the weighted objectives section
        self.objective_page = Objective_Menu(self.master)
        self.objective_page.create_weighted_objectives_section(self.right_frame)

        # Create the DER section
        self.der_page = Der_menu_page(self.master)
        self.der_page.create_der_section(self.right_frame)

        # Create the calculate button
        self.calculate_button = Calculate_Button(self.master, self.location_page)
        self.calculate_button = tk.Button(self.main_frame, text="Calculate", command=self.calculate_button.calculate)
        self.calculate_button.config(font=('Helvetica', 14, 'bold'), bg='black', fg='white')
        self.calculate_button.grid(row=1, column=0, columnspan=2, pady=10)

        # Bind the close event to a custom method
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Handle the window close event."""
        self.master.quit()
        self.master.destroy()




 
if __name__ == "__main__":
    root = tk.Tk()
    app = EnergyResourceApp(root)
    root.mainloop()
