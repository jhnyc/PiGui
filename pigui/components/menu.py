
from PIL import Image, ImageDraw, ImageFont
from pigui.ui.ui import Component
from pigui.hardware.controller import Button, Joystick
from pigui.ui.ui import Document
from pigui.components.camera import CameraApp
from pigui.config import FONT, OFFSET, PADDING
from pigui.components.stats import StatApp
from threading import Thread


menu_items = ["Camera", "Statistic", "Clock", "Something"]

    
class Menu(Component):
    def __init__(self, document: Document, *args, **kwargs):
        super().__init__(document, *args, **kwargs)
        
        self.joystick = Joystick(27, 17, 22)
        # TODO 
        self.prev_cur_position = None
        
        self.cur_position = 1
    
    def render(self):
        image = Image.new("1", (128, 64))
        draw = ImageDraw.Draw(image)
        for i, item in enumerate(menu_items):
            x, y = 0, i*OFFSET
            if i == self.cur_position:
                draw.rectangle(((x, y), (128, y+16)), outline=0, fill=255)
                draw.text((0+PADDING, y), item, font=FONT, fill=0)
            else:
                draw.rectangle(((x, y), (128, y+16)), outline=0, fill=0)
                draw.text((0+PADDING, y), item, font=FONT, fill=255)

        return image
    
    
    def on_click(self):
        cur_item = self.menu_items[self.cur_position]
        print(f"Selected {cur_item}")
        if cur_item == "Camera":
            # TODO Draw starting annimation
            CameraApp(self.document).render()
        elif cur_item == "Statistic":
            StatApp(self.document).render()

    def event_listen(self):
        if self.joystick.on_up:
            self.cur_position = len(self.menu_items) -1 if self.cur_position == 0 else self.cur_position - 1
        elif self.joystick.on_right:
            self.cur_position = 0 if self.cur_position == len(self.menu_items) - 1 else self.cur_position + 1
    