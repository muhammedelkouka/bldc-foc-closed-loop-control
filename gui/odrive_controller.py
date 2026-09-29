import odrive
from odrive.enums import *
import time

class ODriveController:
    def __init__(self):
        self.odrive = None
    
    def connect(self):
        try:
            self.odrive = odrive.find_any()
            print("ODrive connected successfully")
            return True
        except:
            print("Failed to connect to ODrive")
            return False
    
    def is_connected(self):
        return self.odrive is not None
    
    def execute_command(self, command):
        """Execute a raw ODrive command"""
        if not self.is_connected():
            raise Exception("ODrive not connected")
        
        try:
            if '=' in command:
                # Handle assignment
                exec(f"self.odrive.{command}")
                return "Command executed successfully"
            else:
                # Handle query
                return eval(f"self.odrive.{command}")
        except Exception as e:
            raise Exception(f"Command failed: {str(e)}")
    
    def calibrate(self):
        if not self.is_connected():
            return False
        
        try:
            self.odrive.axis0.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
            while self.odrive.axis0.current_state != AXIS_STATE_IDLE:
                time.sleep(0.1)
            
            self.odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            print("Calibration completed")
            return True
        except:
            print("Calibration failed")
            return False
    
    def set_position(self, position):
        if not self.is_connected():
            return
        try:
            self.odrive.axis0.controller.input_pos = float(position)
        except:
            print("Failed to set position")
    
    def set_velocity(self, velocity):
        if not self.is_connected():
            return
        try:
            self.odrive.axis0.controller.input_vel = float(velocity)
        except:
            print("Failed to set velocity")
    
    def get_position(self):
        if not self.is_connected():
            return 0.0
        try:
            return self.odrive.axis0.encoder.pos_estimate
        except:
            return 0.0
    
    def get_velocity(self):
        if not self.is_connected():
            return 0.0
        try:
            return self.odrive.axis0.encoder.vel_estimate
        except:
            return 0.0
    
    def emergency_stop(self):
        if not self.is_connected():
            return
        try:
            self.odrive.axis0.requested_state = AXIS_STATE_IDLE
            print("Emergency stop activated")
        except:
            print("Failed to execute emergency stop")