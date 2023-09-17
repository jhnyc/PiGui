from PIL import Image, ImageDraw, ImageFont
from pigui.ui.ui import Component, EventListener
from pigui.hardware.controller import Button, Joystick
from pigui.ui.ui import Document
from pigui.components.camera import CameraApp
from pigui.config import FONT, OFFSET, PADDING
from pigui.components.stats import StatApp
from threading import Thread




    
class Menu(Component):
    def __init__(self, document: Document):
        super().__init__(document)
        # TODO 
        self.document = document
        self.prev_cur_position = None
        self.menu_items = ["Camera", "Statistic", "Clock", "Something"]
        self.cur_position = 1
        
        evt_cb_tup = [(self.document.controller.joystick.on_press, self.on_click),
                      (self.document.controller.joystick.on_up, self.prev_item),
                      (self.document.controller.joystick.on_right, self.next_item),
                      ]
        
        self.event_listeners.append(EventListener(evt_cb_tup, sleep=0.1))
    
    def render(self):
        image = Image.new("1", (128, 64))
        draw = ImageDraw.Draw(image)
        for i, item in enumerate(self.menu_items):
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
        self.document.goto_frame("stat")
        # if cur_item == "Camera":
        #     # TODO Draw starting annimation
        #     CameraApp(self.document).render()
        # elif cur_item == "Statistic":
        #     StatApp(self.document).render()
        
    def prev_item(self):
        print("pressed Up")
        self.cur_position = len(self.menu_items) -1 if self.cur_position == 0 else self.cur_position - 1
    
    def next_item(self):
        print("pressed Right")
        self.cur_position = 0 if self.cur_position == len(self.menu_items) - 1 else self.cur_position + 1
