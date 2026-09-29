import pyqtgraph as pg
import numpy as np
from collections import deque

class PlotWidget(pg.PlotWidget):
    def __init__(self, title, max_points=500):
        super().__init__()
        self.setBackground('w')
        self.setTitle(title)
        self.showGrid(x=True, y=True)
        
        self.max_points = max_points
        self.data = deque(maxlen=max_points)
        self.times = deque(maxlen=max_points)
        self.start_time = pg.ptime.time()
        
        self.curve = self.plot(pen='b')
    
    def update_plot(self, value):
        current_time = pg.ptime.time() - self.start_time
        self.times.append(current_time)
        self.data.append(value)
        
        self.curve.setData(x=list(self.times), y=list(self.data))