from PIL import ImageFont
OFFSET = 15
PADDING = 5
WIDTH=640
HEIGHT=320
FRAMERATE=30

        
class CustomFont(ImageFont.FreeTypeFont):
    """Wrapper class of ImageFont"""
    def resize(self, size) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(self.path, size)
FONT = CustomFont("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
