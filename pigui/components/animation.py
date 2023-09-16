from PIL import Image, ImageDraw, ImageChops, ImageOps
from pigui.ui.ui import Document
from pigui.config import FONT
import time
from hardware.camera import ImageProcessor


class Animation:
    def camera_flash(self, document: Document):
        document.draw.rectangle(
            (0, 0, document.width, document.height), fill=255, outline=0
        )
        document.render()
        document.draw.rectangle(
            (0, 0, document.width, document.height), fill=0, outline=0
        )
        document.render()
        time.sleep(1)
        document.draw.text((22, 22), "Image saved!", font=FONT, fill=255)
        document.render()

    def unveil(self, document, base_image:Image):
        """Ellipse expands out from the middle unveil the base image"""
        width, height = document.width, document.height
        for frame in range(10):
            # Calculate the radius for the expanding circle
            radius = frame + 9 * frame

            # Calculate the coordinates of the circle's bounding box
            x0, y0 = width // 2 - radius, height // 2 - radius
            x1, y1 = width // 2 + radius, height // 2 + radius

            mask = Image.new("1", (width, height))
            draw = ImageDraw.Draw(mask)
            draw.ellipse([(x0, y0), (x1, y1)], fill=255)

            document.image = ImageChops.logical_and(base_image, mask)
            document.render()
            
        document.draw = ImageDraw.Draw(document.image)

    def landing(self, document: Document):
        img = ImageProcessor.load_img(
            "/home/pi/Desktop/camera/gui/asset/PiOS.png", resize=(128, 64)
        )
        self.unveil(document, img)
