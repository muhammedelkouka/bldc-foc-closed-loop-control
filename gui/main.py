import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import deque
import time
from odrive_controller import ODriveController
from command_panel import CommandPanel

class ODriveGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ODrive Controller_M.Elkouka")
        self.root.geometry("1200x800")
        
        # Initialize ODrive controller
        self.controller = ODriveController()
        
        # Data for plotting
        self.max_points = 100
        self.position_data = deque(maxlen=self.max_points)
        self.velocity_data = deque(maxlen=self.max_points)
        self.time_data = deque(maxlen=self.max_points)
        self.start_time = time.time()
        
        self.create_gui()
        self.setup_plots()
        self.update_plots()
    
    def create_gui(self):
        # Create main container with padding
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel (30% width) for controls
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Right panel (70% width) for plots
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Control Frame
        control_frame = ttk.LabelFrame(left_panel, text="Controls", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Connect Button
        self.connect_btn = ttk.Button(control_frame, text="Connect ODrive", command=self.connect)
        self.connect_btn.pack(fill=tk.X, pady=5)
        
        # Calibrate Button
        self.calibrate_btn = ttk.Button(control_frame, text="Calibrate Motor", command=self.calibrate)
        self.calibrate_btn.pack(fill=tk.X, pady=5)
        
        # Position Control
        pos_frame = ttk.LabelFrame(control_frame, text="Position Control", padding="5")
        pos_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(pos_frame, text="Position:").pack()
        self.pos_var = tk.StringVar(value="0.0")
        self.pos_entry = ttk.Entry(pos_frame, textvariable=self.pos_var)
        self.pos_entry.pack(fill=tk.X, pady=2)
        
        ttk.Button(pos_frame, text="Set Position", 
                  command=lambda: self.controller.set_position(float(self.pos_var.get()))).pack(fill=tk.X)
        
        # Velocity Control
        vel_frame = ttk.LabelFrame(control_frame, text="Velocity Control", padding="5")
        vel_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(vel_frame, text="Velocity:").pack()
        self.vel_var = tk.StringVar(value="0.0")
        self.vel_entry = ttk.Entry(vel_frame, textvariable=self.vel_var)
        self.vel_entry.pack(fill=tk.X, pady=2)
        
        ttk.Button(vel_frame, text="Set Velocity", 
                  command=lambda: self.controller.set_velocity(float(self.vel_var.get()))).pack(fill=tk.X)
        
        # Emergency Stop Button
        stop_btn = ttk.Button(control_frame, text="EMERGENCY STOP", 
                            command=self.controller.emergency_stop, style="Stop.TButton")
        stop_btn.pack(fill=tk.X, pady=20)
        
        # Command Panel
        self.command_panel = CommandPanel(left_panel, self.controller)
        self.command_panel.pack(fill=tk.BOTH, expand=True)
        
        # Configure stop button style
        style = ttk.Style()
        style.configure("Stop.TButton", background="red", foreground="white")
        
        # Add plots to right panel
        self.plot_frame = ttk.Frame(right_panel)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)
    
    def setup_plots(self):
        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 6))
        
        # Position subplot
        self.pos_plot = self.fig.add_subplot(211)
        self.pos_plot.set_title("Position")
        self.pos_plot.grid(True)
        self.pos_line, = self.pos_plot.plot([], [], 'b-')
        
        # Velocity subplot
        self.vel_plot = self.fig.add_subplot(212)
        self.vel_plot.set_title("Velocity")
        self.vel_plot.grid(True)
        self.vel_line, = self.vel_plot.plot([], [], 'r-')
        
        # Create canvas and add to right panel
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.fig.tight_layout()
    
    def connect(self):
        if self.controller.connect():
            self.connect_btn.configure(text="Connected", state="disabled")
    
    def calibrate(self):
        self.controller.calibrate()
    
    def update_plots(self):
        if self.controller.is_connected():
            current_time = time.time() - self.start_time
            self.time_data.append(current_time)
            
            # Update position data
            pos = self.controller.get_position()
            self.position_data.append(pos)
            
            # Update velocity data
            vel = self.controller.get_velocity()
            self.velocity_data.append(vel)
            
            # Update plots
            self.pos_line.set_data(list(self.time_data), list(self.position_data))
            self.vel_line.set_data(list(self.time_data), list(self.velocity_data))
            
            # Adjust plot limits
            for plot in [self.pos_plot, self.vel_plot]:
                plot.relim()
                plot.autoscale_view()
            
            self.canvas.draw()
        
        # Schedule next update
        self.root.after(100, self.update_plots)

def main():
    root = tk.Tk()
    app = ODriveGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()