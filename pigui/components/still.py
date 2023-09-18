from PIL import Image, ImageDraw
from abc import ABC, abstractmethod


class Still(ABC):
    def text(text: str):
        image = Image.new("1", (128, 64))
        draw = ImageDraw.Draw(image)
        draw.text((0, 27), text, fill=255)
        return image
