from pigui.ui.ui import Component
from datetime import datetime
from PIL import Image, ImageDraw
from threading import Thread
WIDTH = 128
HEIGHT = 16


class Header(Component):
    def __init__(self, document, height):
        super().__init__(document, height)        
    
    def render(self):
        image = Image.new("1", (128, 64))
        draw = ImageDraw.Draw(image)

        draw.rectangle((0,0, 128, 16), fill=255)
        dt_string = datetime.now().strftime("%H:%M:%S   %d-%b")
        draw.text((3, 1), f"PiOS    {dt_string}", font=self.document.font.resize(10), fill=0)
        return image
    
    