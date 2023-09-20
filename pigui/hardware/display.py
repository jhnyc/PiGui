import board
import busio
import adafruit_ssd1306
from PIL import Image


class Display:
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

    def clear_display(self):
        self.display.fill(0)
        self.display.show()

    def display_img(self, img: Image, clear=False):
        if clear:
            self.clear_display()
        self.display.image(img)
        self.display.show()
