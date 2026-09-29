import tkinter as tk
from tkinter import ttk, scrolledtext

class CommandPanel(ttk.LabelFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, text="ODrive Commands", padding="10")
        self.controller = controller
        
        # Command input
        self.command_input = ttk.Entry(self)
        self.command_input.pack(fill=tk.X, pady=2)
        self.command_input.bind('<Return>', self.execute_command)
        
        # Send button
        send_btn = ttk.Button(self, text="Send Command", command=self.execute_command)
        send_btn.pack(fill=tk.X, pady=2)
        
        # Quick command buttons
        self.create_quick_commands()
        
        # Output display
        self.output_text = scrolledtext.ScrolledText(self, height=10)
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Add common commands help
        self.show_output("Common ODrive Commands:\n" +
                        "- axis0.requested_state = AXIS_STATE_IDLE\n" +
                        "- axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL\n" +
                        "- axis0.motor.config.pole_pairs = 15\n" +
                        "- axis0.motor.config.resistance_calib_max_voltage = 4\n" +
                        "- save_configuration()\n" +
                        "- reboot()")
    
    def create_quick_commands(self):
        quick_commands_frame = ttk.LabelFrame(self, text="Quick Commands", padding="5")
        quick_commands_frame.pack(fill=tk.X, pady=5)
        
        commands = [
            ("Erase Config", "erase_configuration()"),
            ("Save Config", "save_configuration()"),
            ("Reboot", "reboot()"),
            ("Close Loop", "axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL"),
            ("Idle", "axis0.requested_state = AXIS_STATE_IDLE")
        ]
        
        for label, cmd in commands:
            btn = ttk.Button(quick_commands_frame, text=label,
                           command=lambda c=cmd: self.execute_quick_command(c))
            btn.pack(fill=tk.X, pady=1)
    
    def execute_quick_command(self, command):
        self.command_input.delete(0, tk.END)
        self.command_input.insert(0, command)
        self.execute_command()
    
    def execute_command(self, event=None):
        if not self.controller.is_connected():
            self.show_output("Error: ODrive not connected")
            return
            
        command = self.command_input.get().strip()
        if not command:
            return
            
        try:
            result = self.controller.execute_command(command)
            if result is not None:
                self.show_output(f"> {command}\n{result}")
            else:
                self.show_output(f"> {command}\nCommand executed successfully")
        except Exception as e:
            self.show_output(f"Error: {str(e)}")
            
        self.command_input.delete(0, tk.END)
    
    def show_output(self, text):
        self.output_text.insert(tk.END, f"{text}\n")
        self.output_text.see(tk.END)