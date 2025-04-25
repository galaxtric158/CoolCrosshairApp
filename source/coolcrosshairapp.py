import tkinter as tk
from tkinter import colorchooser, ttk, filedialog
import json
import os
import math
import win32gui
import win32con
import win32api

#shoutout to mr rayhan for teaching me like allis (especially classes)
class CoolCrosshairApp:
    def __init__(self):
        self.visible = True
        self.crosshair_color = "#FF0000"
        self.crosshair_size = 10
        self.crosshair_shape = "Cross"
        self.rotation_angle = 0  # Starting angle
        self.center_gap = False  # Option for center gap (like Valorant/CS:GO)
        self.center_dot = False  # Option for center dot

        # Initialize the main window for the overlay
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.geometry(f"{win32api.GetSystemMetrics(0)}x{win32api.GetSystemMetrics(1)}+0+0")
        self.root.attributes("-topmost", True)

        # Remove background and use transparency instead
        self.root.config(bg="black")

        # Create a canvas for the crosshair
        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Create settings window with scrollable frame
        self.create_settings_gui()

        # Draw the initial crosshair
        self.draw_crosshair()

        # Make the window click-through
        self.make_clickthrough()

    def create_settings_gui(self):
        """Create the settings window with scrollable content."""
        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("CoolCrosshairApp Settings")
        self.settings_window.geometry("350x500")

        # Create a Canvas widget for scrolling
        canvas = tk.Canvas(self.settings_window)
        canvas.pack(side="left", fill="both", expand=True)

        # Add a Scrollbar to the Canvas
        scrollbar = tk.Scrollbar(self.settings_window, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        # Create a frame inside the canvas to hold all the controls
        settings_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=settings_frame, anchor="nw")

        # Link the scrollbar to the canvas
        canvas.configure(yscrollcommand=scrollbar.set)

        # Frame for controls (center them)
        controls_frame = tk.Frame(settings_frame)
        controls_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Size slider
        tk.Label(controls_frame, text="Size", font=("Arial", 12)).pack(pady=5)
        self.size_var = tk.DoubleVar(value=self.crosshair_size)
        size_slider = tk.Scale(controls_frame, from_=0.1, to=50, orient="horizontal", variable=self.size_var, resolution=0.1, command=self.update_crosshair)
        size_slider.pack(fill="x", pady=5)

        # Rotation slider
        tk.Label(controls_frame, text="Rotation (°)", font=("Arial", 12)).pack(pady=5)
        self.rotation_var = tk.IntVar(value=self.rotation_angle)
        rotation_slider = tk.Scale(controls_frame, from_=0, to=360, orient="horizontal", variable=self.rotation_var, command=self.update_crosshair)
        rotation_slider.pack(fill="x", pady=5)

        # Color picker button
        color_button = tk.Button(controls_frame, text="Pick Color", command=self.pick_color, width=20)
        color_button.pack(pady=10)

        # Shape dropdown
        tk.Label(controls_frame, text="Shape", font=("Arial", 12)).pack(pady=5)
        shapes = ["Dot", "Cross", "Circle", "Square", "Triangle", "Pentagon"]
        self.shape_var = tk.StringVar(value=self.crosshair_shape)
        shape_dropdown = ttk.Combobox(controls_frame, values=shapes, textvariable=self.shape_var, state="readonly", width=17)
        shape_dropdown.pack(pady=5)
        shape_dropdown.bind("<<ComboboxSelected>>", self.update_crosshair)  # Update on shape selection change

        # Center gap checkbox
        self.center_gap_var = tk.BooleanVar(value=self.center_gap)
        center_gap_check = tk.Checkbutton(controls_frame, text="Center Gap", variable=self.center_gap_var, command=self.update_crosshair)
        center_gap_check.pack(pady=5)

        # Center dot checkbox
        self.center_dot_var = tk.BooleanVar(value=self.center_dot)
        center_dot_check = tk.Checkbutton(controls_frame, text="Center Dot", variable=self.center_dot_var, command=self.update_crosshair)
        center_dot_check.pack(pady=5)

        # Show/Hide toggle button
        self.toggle_btn = tk.Button(controls_frame, text="Hide Crosshair", command=self.toggle_visibility, width=20)
        self.toggle_btn.pack(pady=10)

        # Save/Load buttons
        save_button = tk.Button(controls_frame, text="Save Config", command=self.save_config, width=20)
        save_button.pack(pady=5)
        load_button = tk.Button(controls_frame, text="Load Config", command=self.load_config, width=20)
        load_button.pack(pady=5)

        # Update the scrollable area after all widgets are added
        settings_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def pick_color(self):
        """Open the color picker dialog."""
        color = colorchooser.askcolor(title="Pick Crosshair Color")
        if color[1]:
            self.crosshair_color = color[1]
            self.update_crosshair()

    def draw_crosshair(self):
        """Draw the crosshair based on current settings."""
        self.canvas.delete("all")
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = screen_w // 2
        y = screen_h // 2

        size = self.crosshair_size
        color = self.crosshair_color
        shape = self.crosshair_shape
        angle = math.radians(self.rotation_angle)  # Convert angle to radians

        # Coordinates for rotation
        x1 = x - size
        y1 = y - size
        x2 = x + size
        y2 = y + size

        # Draw crosshair shape
        if self.center_gap:  # If the gap option is enabled, skip drawing in the center
            if shape == "Dot":
                self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="")
            elif shape == "Cross":
                # Only draw lines outside the gap area
                self.create_rotated_line(x, y, x - size, y, x - size / 2, y, angle, color)
                self.create_rotated_line(x, y, x + size, y, x + size / 2, y, angle, color)
                self.create_rotated_line(x, y, x, y - size, x, y - size / 2, angle, color)
                self.create_rotated_line(x, y, x, y + size, x, y + size / 2, angle, color)
            elif shape == "Circle":
                self.canvas.create_oval(x1, y1, x2, y2, outline=color, width=2)
            elif shape == "Square":
                self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2)
            elif shape == "Triangle":
                self.canvas.create_polygon(x, y-size, x-size, y+size, x+size, y+size, outline=color, width=2)
            elif shape == "Pentagon":
                self.draw_pentagon(x, y, size, angle, color)
        else:
            # Draw crosshair with no gap (normal crosshair behavior)
            if shape == "Dot":
                self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="")
            elif shape == "Cross":
                # Draw lines normally for Cross
                self.create_rotated_line(x, y, x - size, y, x + size, y, angle, color)
                self.create_rotated_line(x, y, x, y - size, x, y + size, angle, color)
            elif shape == "Circle":
                self.canvas.create_oval(x1, y1, x2, y2, outline=color, width=2)
            elif shape == "Square":
                self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2)
            elif shape == "Triangle":
                self.canvas.create_polygon(x, y-size, x-size, y+size, x+size, y+size, outline=color, width=2)
            elif shape == "Pentagon":
                self.draw_pentagon(x, y, size, angle, color)

        # Draw center dot if enabled
        if self.center_dot:
            self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill=color, outline="")

    def draw_pentagon(self, x, y, size, angle, color):
        """Draw a rotated pentagon."""
        # Calculate the coordinates of the pentagon vertices
        points = []
        for i in range(5):
            theta = math.radians(72 * i + 90 + math.degrees(angle))  # 72 degrees apart
            px = x + size * math.cos(theta)
            py = y + size * math.sin(theta)
            points.append((px, py))

        self.canvas.create_polygon(points, outline=color, width=2)

    def create_rotated_line(self, x, y, x1, y1, x2, y2, angle, color):
        """Create a rotated line."""
        # Calculate rotated coordinates
        x1_rot = x + (x1 - x) * math.cos(angle) - (y1 - y) * math.sin(angle)
        y1_rot = y + (x1 - x) * math.sin(angle) + (y1 - y) * math.cos(angle)
        x2_rot = x + (x2 - x) * math.cos(angle) - (y2 - y) * math.sin(angle)
        y2_rot = y + (x2 - x) * math.sin(angle) + (y2 - y) * math.cos(angle)
        self.canvas.create_line(x1_rot, y1_rot, x2_rot, y2_rot, fill=color, width=2)

    def update_crosshair(self, *_):
        """Update the crosshair when settings change."""
        self.crosshair_size = self.size_var.get()
        self.rotation_angle = self.rotation_var.get()
        self.crosshair_shape = self.shape_var.get()
        self.center_gap = self.center_gap_var.get()  # Update the gap setting
        self.center_dot = self.center_dot_var.get()  # Update the center dot setting

        # Redraw the crosshair
        self.draw_crosshair()

    def toggle_visibility(self):
        """Toggle the visibility of the crosshair."""
        self.visible = not self.visible
        if self.visible:
            self.toggle_btn.config(text="Hide Crosshair")
        else:
            self.toggle_btn.config(text="Show Crosshair")
        self.canvas.itemconfig("all", state="normal" if self.visible else "hidden")

    def save_config(self):
        """Save the current settings to a .cca file."""
        config = {
            "crosshair_color": self.crosshair_color,
            "crosshair_size": self.crosshair_size,
            "crosshair_shape": self.crosshair_shape,
            "rotation_angle": self.rotation_angle,
            "center_gap": self.center_gap,
            "center_dot": self.center_dot,
        }

        file_path = filedialog.asksaveasfilename(defaultextension=".cca", filetypes=[("Crosshair Config", "*.cca")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(config, f)

    def load_config(self):
        """Load settings from a .cca file."""
        file_path = filedialog.askopenfilename(defaultextension=".cca", filetypes=[("Crosshair Config", "*.cca")])
        if file_path:
            with open(file_path, 'r') as f:
                config = json.load(f)

            self.crosshair_color = config["crosshair_color"]
            self.crosshair_size = config["crosshair_size"]
            self.crosshair_shape = config["crosshair_shape"]
            self.rotation_angle = config["rotation_angle"]
            self.center_gap = config["center_gap"]
            self.center_dot = config["center_dot"]

            # Update UI elements
            self.size_var.set(self.crosshair_size)
            self.rotation_var.set(self.rotation_angle)
            self.shape_var.set(self.crosshair_shape)
            self.center_gap_var.set(self.center_gap)
            self.center_dot_var.set(self.center_dot)

            self.update_crosshair()

    def make_clickthrough(self):
        """Make the window click-through."""
        hwnd = win32gui.GetParent(self.root.winfo_id())
        exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exstyle | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)


if __name__ == "__main__":
    app = CoolCrosshairApp()
    app.root.mainloop()

#thanks for using my crosshair app wowowoowwowow <3
