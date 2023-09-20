from pigui.hardware.camera import Camera, ImageProcessor
from pigui.hardware.controller import Button, Joystick
from pigui.ui import Component, Document, EventListener
from pigui.components.still import Still
import time
import os


class CameraApp(Component):
    def __init__(self, document: Document, image_directory="."):
        super().__init__(document)
        self.camera = None
        self.image_directory = image_directory
        self.is_capturing_image = False

        # Return to menu page
        return_listener = EventListener(
            [(self.document.controller.joystick.on_up, self.close_cam)],
            sleep=0.1,
            debounce=0.5,
        )
        # Capture image
        capture_listener = EventListener(
            [(self.document.controller.joystick.on_press, self.capture_img)],
            sleep=0.1,
            debounce=0.5,
        )
        self.register_event_listener([return_listener, capture_listener])

    def close_cam(self):
        # Return to menu page
        self.document.goto_frame("menu")

        # Turn off camera
        if self.camera:
            self.camera.close()
            self.camera = None
            print("Camera closed.")

    def capture_img(self):
        if self.camera and not self.is_capturing_image:
            self.is_capturing_image = True

            img_name = self.get_image_name()
            self.camera.capture_image(img_name)
            print(f"Image {img_name} saved!")

            self.is_capturing_image = False

    def render(self):
        if self.camera is None:
            self.camera = Camera()

        # Taking image
        if self.is_capturing_image:
            return Still.text("Saving image.....")

        # Previewing
        try:
            frame = next(self.camera.video_stream())
            return ImageProcessor.load_img(frame.array)
        except:
            return None

    def get_image_name(self, prefix="IMG"):
        image_files = os.listdir(self.image_directory)
        image_files = [f for f in image_files if f.startswith(prefix)]
        image_num = (
            0
            if not image_files
            else max([int(f.split(prefix)[1].split(".jpg")[0]) for f in image_files])
        )
        img_name = f"{prefix}{image_num + 1}.jpg"
        return img_name
