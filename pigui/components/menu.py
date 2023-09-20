from PIL import Image, ImageDraw
from pigui.ui import Component, Document, EventListener
from pigui.utils.constants import *


class Menu(Component):
    def __init__(self, document: Document):
        super().__init__(document)
        self.document = document
        self.prev_cur_position = None
        self.menu_items = ["Camera", "Statistic", "Clock", "Draw"]
        self.cur_position = 1

        evt_cb_tup = [
            (self.document.controller.joystick.on_press, self.on_click),
            (self.document.controller.joystick.on_up, self.prev_item),
            (self.document.controller.joystick.on_right, self.next_item),
        ]

        self.event_listeners.append(EventListener(evt_cb_tup, sleep=0.1, debounce=0.5))

    def render(self):
        image = Image.new("1", (128, 64))
        draw = ImageDraw.Draw(image)
        for i, item in enumerate(self.menu_items):
            x, y = 0, i * text_line_height_px
            if i == self.cur_position:
                draw.rectangle(((x, y), (128, y + 16)), outline=0, fill=255)
                draw.text((0 + text_left_padding, y), item, font=font, fill=0)
            else:
                draw.rectangle(((x, y), (128, y + 16)), outline=0, fill=0)
                draw.text((0 + text_left_padding, y), item, font=font, fill=255)

        return image

    def on_click(self):
        cur_item = self.menu_items[self.cur_position]
        print(f"Selected {cur_item}")
        if cur_item == "Camera":
            self.document.goto_frame("camera")
        elif cur_item == "Statistic":
            self.document.goto_frame("stat")
        elif cur_item == "Draw":
            self.document.goto_frame("draw")

    def prev_item(self):
        print("pressed Up")
        self.cur_position = (
            len(self.menu_items) - 1
            if self.cur_position == 0
            else self.cur_position - 1
        )

    def next_item(self):
        print("pressed Right")
        self.cur_position = (
            0
            if self.cur_position == len(self.menu_items) - 1
            else self.cur_position + 1
        )
