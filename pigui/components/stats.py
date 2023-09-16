from pigui.ui.ui import Component, Document, State, EventListener
from pigui.config import HEIGHT, WIDTH, FONT
import subprocess
from PIL import Image,ImageDraw
from threading import Thread
import psutil


class StatApp(Component):
    def __init__(self):
        super().__init__()
        self.ip = State("")
        self.cpu = State("")
        self.mem = State("")
        self.disk = State("")
        self.font = FONT
        
        self.event_listeners.append(EventListener(events=[True], callbacks=[self.update_sys_info], sleep=2))
        
    def __repr__(self):
        return f"{self.ip} {self.cpu}"

    def render(self) -> Image:
        image = Image.new("1", (128, 64))
        draw = ImageDraw.Draw(image)
        
        padding = 0
        top = padding
        x = 0
        # Write four lines of text.
        draw.text((x, top + 0), f"IP: {self.ip.state}", font=self.font, fill=255)
        draw.text((x, top + 16), f"CPU: {self.cpu.state}", font=self.font, fill=255)
        draw.text((x, top + 32), f"RAM: {self.mem.state}", font=self.font, fill=255)
        draw.text((x, top + 48), f"DISK: {self.disk.state}", font=self.font, fill=255)
        return image
    
    def update_sys_info(self):
        IP, CPU, RAM, DISK = self.get_sys_info()
        self.ip.update(IP)
        self.cpu.update(CPU)
        self.mem.update(RAM)
        self.disk.update(DISK)
    
    def get_sys_info(self):
        IP = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True).decode("utf-8")
        CPU = psutil.cpu_percent()
        RAM = psutil.virtual_memory()[2]
        DISK = 100 - psutil.disk_usage('/').percent
        return IP, CPU, RAM, DISK

    
    
    
                