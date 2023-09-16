import time
from PIL import Image
from pigui.ui.ui import Component
from pigui.hardware.controller import Joystick
import numpy as np

class DrawApp(Component):
    def __init__(self, document):
        super().__init__(document)
        self.cursor_x, self.cursor_y = 128//2, 64//2
        self.prev_cursor_x, self.prev_cursor_y = 128//2, 64//2
        self.is_edit_mode = True
        self.pixel = np.ones((64,128), dtype=int)
        self.pixel.fill(255)
        
        self.joystick = Joystick(27, 17, 22)

    
    def render(self):
        # TODO
        self.update_pixel()
        return Image.fromarray(self.pixel).convert('1')
        
        
    def update_pixel(self):
        # Clear previous cursor 
        if not self.is_edit_mode:
            self.pixel[self.prev_cursor_y][self.prev_cursor_x] = 255
        
        # Show cursor
        self.pixel[self.cursor_y][self.cursor_x] = 0
        
        self.prev_cursor_x, self.prev_cursor_y = self.cursor_x, self.cursor_y
            
    
    def save_drawing(self):
        Image.fromarray(self.pixel).convert('1').save("Drawing.png")
        
    def event_listen(self):
        if self.joystick.on_up:
            self.cursor_y += 1
        elif self.joystick.on_right:
            self.cursor_x += 1
        elif self.joystick.on_press:
            self.save_drawing()
    