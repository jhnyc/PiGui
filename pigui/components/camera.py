from pigui.hardware.camera import Camera, ImageProcessor
from pigui.hardware.controller import Button, Joystick
from pigui.ui.ui import Component, Document
import time


class CameraApp(Component):
    def __init__(self, document: Document):
        super().__init__(document)
        self.camera = Camera()
        self.is_on = True
        button = Button(4)
        button.event_listener(callback_fn=self.close_cam)
        joystick = Joystick(27, 17, 22)
    
    
    def close_cam(self):
        self.is_on = False
        self.camera.camera.close()
        
    def render(self):
        for frame in self.camera.capture_video_stream():
            self.document.image = ImageProcessor.load_img(frame.array, resize=(128,64))
            self.document.render()
            time.sleep(0.03)