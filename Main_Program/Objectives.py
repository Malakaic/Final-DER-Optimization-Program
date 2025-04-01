import csv
import os
import tkinter as tk
import config
import requests
from tkinter import filedialog, messagebox, ttk 


class Objective_Menu(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Access global weights from config.py
        self.financial_weight = config.financial_weight
        self.efficiency_weight = config.efficiency_weight
        self.sustainability_weight = config.sustainability_weight
        self.power_quality_weight = config.power_quality_weight
        
    def create_weighted_objectives_section(self, frame):
            """Creates a weighted objectives section with sliders that always add up to 100 and a Save button."""

            def update_sliders(changed_slider):
                """Adjusts the remaining sliders to ensure their sum stays at 100 when one is changed."""
                sliders = {
                    "financial": self.financial_slider,
                    "efficiency": self.efficiency_slider,
                    "sustainability": self.sustainability_slider,
                    "power_quality": self.power_quality_slider
                }

                # Get current values of all sliders
                values = {key: slider.get() for key, slider in sliders.items()}
                total = sum(values.values())

                # Adjust only if the total isn't 100
                if total != 100:
                    remaining_keys = [key for key in sliders.keys() if key != changed_slider]
                    remaining_sum = sum(values[key] for key in remaining_keys)

                    if remaining_sum > 0:
                        # Scale down/up the other sliders proportionally
                        scale_factor = (100 - values[changed_slider]) / remaining_sum
                        for key in remaining_keys:
                            sliders[key].set(int(values[key] * scale_factor))
                    else:
                        # If the remaining sum is zero, just distribute the rest evenly
                        split_value = (100 - values[changed_slider]) / len(remaining_keys)
                        for key in remaining_keys:
                            sliders[key].set(int(split_value))

            def check_and_fix_99():
                """If the total is 99, prompt the user to check a box for which objective should get +1%"""
                sliders = {
                    "Financial": self.financial_slider,
                    "Efficiency": self.efficiency_slider,
                    "Sustainability": self.sustainability_slider,
                    "Power Quality": self.power_quality_slider
                }

                values = {key: slider.get() for key, slider in sliders.items()}
                total = sum(values.values())

                if total == 99:
                    # Create a popup window
                    popup = tk.Toplevel()
                    popup.title("Adjust Objective")
                    popup.geometry("350x200")
                    popup.grab_set()  # Make the window modal
                    
                    tk.Label(popup, text="The total is 99%. Select an objective to receive +1%, and save:").pack(pady=10)

                    # Variables to track selected checkbox
                    selected_var = tk.StringVar()

                    def apply_selection():
                        """Applies the selection and updates the corresponding slider."""
                        choice = selected_var.get()
                        if choice and choice in sliders:
                            sliders[choice].set(sliders[choice].get() + 1)
                            popup.destroy()
                        else:
                            messagebox.showerror("Invalid Choice", "Please select an objective before applying.")

                    # Create checkboxes
                    for key in sliders.keys():
                        tk.Radiobutton(popup, text=key, variable=selected_var, value=key).pack(anchor="w")

                    # Apply button
                    tk.Button(popup, text="Apply", command=apply_selection).pack(pady=10)

            def save_values():
                """Stores the current slider values in global variables and ensures they sum to 100."""
                global financial_weight, efficiency_weight, sustainability_weight, power_quality_weight

                # Check for the 99% issue
                check_and_fix_99()

                # Save the values
                config.financial_weight = self.financial_slider.get()
                config.efficiency_weight = self.efficiency_slider.get()
                config.sustainability_weight = self.sustainability_slider.get()
                config.power_quality_weight = self.power_quality_slider.get()
                
                print("Values Saved:")
                print(f"Financial: {config.financial_weight}")
                print(f"Efficiency: {config.efficiency_weight}")
                print(f"Sustainability: {config.sustainability_weight}")
                print(f"Power Quality: {config.power_quality_weight}")

            # Create the LabelFrame
            objectives_frame = ttk.LabelFrame(frame, text="Weighted Objectives", height=250, width=400)
            objectives_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

            # Set grid weight for resizing
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)

            # Create Sliders
            tk.Label(objectives_frame, text="Financial:").grid(row=0, column=0, padx=5)
            self.financial_slider = tk.Scale(objectives_frame, from_=0, to=100, orient="horizontal", length=300, 
                                            command=lambda event: update_sliders("financial"))
            self.financial_slider.grid(row=0, column=1, padx=5)

            tk.Label(objectives_frame, text="Efficiency:").grid(row=1, column=0, padx=5)
            self.efficiency_slider = tk.Scale(objectives_frame, from_=0, to=100, orient="horizontal", length=300, 
                                            command=lambda event: update_sliders("efficiency"))
            self.efficiency_slider.grid(row=1, column=1, padx=5)

            tk.Label(objectives_frame, text="Sustainability:").grid(row=2, column=0, padx=5)
            self.sustainability_slider = tk.Scale(objectives_frame, from_=0, to=100, orient="horizontal", length=300, 
                                                command=lambda event: update_sliders("sustainability"))
            self.sustainability_slider.grid(row=2, column=1, padx=5)

            tk.Label(objectives_frame, text="Power Quality:").grid(row=3, column=0, padx=5)
            self.power_quality_slider = tk.Scale(objectives_frame, from_=0, to=100, orient="horizontal", length=300, 
                                                command=lambda event: update_sliders("power_quality"))
            self.power_quality_slider.grid(row=3, column=1, padx=5)

            # Save Button
            save_button = tk.Button(objectives_frame, text="Save", command=save_values)
            save_button.grid(row=4, column=0, columnspan=2, pady=10)

            # Set grid row configurations
            for i in range(4):
                objectives_frame.grid_rowconfigure(i, weight=1)

            # Initialize sliders to sum to 100
            self.financial_slider.set(self.financial_weight)
            self.efficiency_slider.set(self.efficiency_weight)
            self.sustainability_slider.set(self.sustainability_weight)
            self.power_quality_slider.set(self.power_quality_weight)