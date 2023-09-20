import time
import numpy as np
from PIL import Image
from pigui.hardware.controller import Joystick
from pigui.ui import Component, EventListener


class DrawApp(Component):
    def __init__(self, document):
        super().__init__(document)
        self.cursor_x, self.cursor_y = 128 // 2, 64 // 2
        self.prev_cursor_x, self.prev_cursor_y = 128 // 2, 64 // 2
        self.is_edit_mode = True
        self.pixel = np.ones((64, 128), dtype=int)
        self.pixel.fill(255)

        evt_cb = [
            (self.document.controller.joystick.on_up, self.cursor_on_up),
            (self.document.controller.joystick.on_right, self.cursor_on_right),
            (self.document.controller.joystick.on_press, self.save_drawing),
            (self.document.controller.button.on_press, self.toggle_edit_mode),
        ]

        self.register_event_listener(EventListener(evt_cb, sleep=0.05))

    def render(self):
        return Image.fromarray(self.pixel).convert("1")

    def update_pixel(self):
        # Clear previous cursor
        if self.is_edit_mode:
            self.pixel[self.cursor_y][self.cursor_x] = 0

    def save_drawing(self):
        Image.fromarray(self.pixel).convert("1").save("Drawing.png")

    def cursor_on_up(self):
        pos = self.cursor_y - 1
        self.cursor_y = pos if pos >= 0 else 63
        self.update_pixel()

    def cursor_on_right(self):
        pos = self.cursor_x + 1
        self.cursor_x = pos if pos < 128 else 0
        self.update_pixel()

    def toggle_edit_mode(self):
        self.is_edit_mode = not self.is_edit_mode
