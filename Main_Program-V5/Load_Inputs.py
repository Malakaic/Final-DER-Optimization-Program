import csv
import os
import tkinter as tk
import requests
from tkinter import filedialog, ttk 
import Menu_Bar
import config


class LoadDemandSection(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.master = parent

    def create_load_demand_section(self, frame):
        """Creates a load demand section."""
        load_frame = ttk.LabelFrame(frame, text="Load Demand")
        load_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)  # CHANGED row=2 -> row=1

        # Monthly entries
        self.monthly_entries = {}
        for i, month in enumerate(["January", "February", "March", "April", "May", "June", 
                                   "July", "August", "September", "October", "November", "December"], start=0):  # CHANGED start=2 -> start=0
            tk.Label(load_frame, text=f"{month}:").grid(row=i, column=0, padx=5)
            entry = tk.Entry(load_frame)
            entry.grid(row=i, column=1, padx=5)
            self.monthly_entries[month] = entry
        
       


        

        # Create a new grid rate input section below monthly entries
        tk.Label(load_frame, text="Grid Rate ($/kWh):").grid(row=12, column=0, padx=5, pady=(10, 0))  # CHANGED row=13 -> row=12
        self.grid_rate_entry = tk.Entry(load_frame)
        self.grid_rate_entry.grid(row=13, column=1, padx=5)  # CHANGED row=14 -> row=13

        # Properly configure row stretching to allow space for both sections
        frame.grid_rowconfigure(0, weight=1)  # Location Section
        frame.grid_rowconfigure(1, weight=1)  # Load Demand Section

        # Function to save the load demand values to config
        def save_load_demand():
            config.load_demand = [float(self.monthly_entries[month].get() or 0) for month in self.monthly_entries]
            config.grid_rate = float(self.grid_rate_entry.get() or 0)
            print("Load demand saved:", config.load_demand)  # Debugging output
            print("Grid rate saved:", config.grid_rate)

        # Add a button to save the load demand
        save_button = tk.Button(load_frame, text="Save Load Demand", command=save_load_demand)
        save_button.grid(row=14, column=0, columnspan=2, pady=10)
