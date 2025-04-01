import tkinter as tk
import config
from tkinter import messagebox, ttk 

class Objective_Menu(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Access global weights from config.py
        self.cost_weight = config.cost_weight
        self.renewable_weight = config.renewable_weight
        
    def create_weighted_objectives_section(self, frame):
        """Creates a weighted objectives section with sliders that always add up to 100."""
        
        def update_sliders(changed_slider):
            """Ensures the two sliders always sum to 100."""
            if changed_slider == "cost":
                self.renewable_slider.set(100 - self.cost_slider.get())
            else:
                self.cost_slider.set(100 - self.renewable_slider.get())
        
        def save_values():
            """Stores the current slider values in global variables."""
            config.cost_weight = self.cost_slider.get()
            config.renewable_weight = self.renewable_slider.get()
            print("Values Saved:")
            print(f"Cost: {config.cost_weight}")
            print(f"Renewable: {config.renewable_weight}")

        # Create the LabelFrame
        objectives_frame = ttk.LabelFrame(frame, text="Weighted Objectives", height=150, width=400)
        objectives_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Create Sliders
        tk.Label(objectives_frame, text="Cost:").grid(row=0, column=0, padx=5)
        self.cost_slider = tk.Scale(objectives_frame, from_=0, to=100, orient="horizontal", length=300, 
                                    command=lambda event: update_sliders("cost"))
        self.cost_slider.grid(row=0, column=1, padx=5)

        tk.Label(objectives_frame, text="Renewable:").grid(row=1, column=0, padx=5)
        self.renewable_slider = tk.Scale(objectives_frame, from_=0, to=100, orient="horizontal", length=300, 
                                         command=lambda event: update_sliders("renewable"))
        self.renewable_slider.grid(row=1, column=1, padx=5)

        # Save Button
        save_button = tk.Button(objectives_frame, text="Save", command=save_values)
        save_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Initialize sliders to sum to 100
        self.cost_slider.set(self.cost_weight)
        self.renewable_slider.set(100 - self.cost_weight)
