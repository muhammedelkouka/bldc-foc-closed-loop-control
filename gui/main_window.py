from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSpinBox, QDoubleSpinBox
)
from PyQt6.QtCore import QTimer
import pyqtgraph as pg
from odrive_controller import ODriveController
from plot_widget import PlotWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ODrive Controller")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize ODrive controller
        self.controller = ODriveController()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create control panel
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)
        
        # Create plots
        plots_widget = self.create_plots()
        layout.addWidget(plots_widget)
        
        # Setup update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(100)  # Update every 100ms
    
    def create_control_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Connection controls
        connect_btn = QPushButton("Connect ODrive")
        connect_btn.clicked.connect(self.controller.connect)
        layout.addWidget(connect_btn)
        
        # Motor controls
        calibrate_btn = QPushButton("Calibrate Motor")
        calibrate_btn.clicked.connect(self.controller.calibrate)
        layout.addWidget(calibrate_btn)
        
        # Position control
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("Position:"))
        self.pos_input = QDoubleSpinBox()
        self.pos_input.setRange(-100000, 100000)
        pos_layout.addWidget(self.pos_input)
        set_pos_btn = QPushButton("Set Position")
        set_pos_btn.clicked.connect(lambda: self.controller.set_position(self.pos_input.value()))
        pos_layout.addWidget(set_pos_btn)
        layout.addLayout(pos_layout)
        
        # Velocity control
        vel_layout = QHBoxLayout()
        vel_layout.addWidget(QLabel("Velocity:"))
        self.vel_input = QDoubleSpinBox()
        self.vel_input.setRange(-100000, 100000)
        vel_layout.addWidget(self.vel_input)
        set_vel_btn = QPushButton("Set Velocity")
        set_vel_btn.clicked.connect(lambda: self.controller.set_velocity(self.vel_input.value()))
        vel_layout.addWidget(set_vel_btn)
        layout.addLayout(vel_layout)
        
        # Emergency stop
        stop_btn = QPushButton("STOP")
        stop_btn.setStyleSheet("background-color: red; color: white;")
        stop_btn.clicked.connect(self.controller.emergency_stop)
        layout.addWidget(stop_btn)
        
        layout.addStretch()
        return panel
    
    def create_plots(self):
        plots = QWidget()
        layout = QVBoxLayout(plots)
        
        # Position plot
        self.position_plot = PlotWidget("Position")
        layout.addWidget(self.position_plot)
        
        # Velocity plot
        self.velocity_plot = PlotWidget("Velocity")
        layout.addWidget(self.velocity_plot)
        
        return plots
    
    def update_plots(self):
        if self.controller.is_connected():
            pos = self.controller.get_position()
            vel = self.controller.get_velocity()
            
            self.position_plot.update_plot(pos)
            self.velocity_plot.update_plot(vel)