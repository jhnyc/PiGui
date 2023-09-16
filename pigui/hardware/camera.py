import picamera
from picamera.array import PiRGBArray
from pigui.config import WIDTH, HEIGHT, FRAMERATE
from io import BytesIO
from typing import Union, Generator
from PIL import Image, ImageFont
from numpy import ndarray

class Camera:
    def __init__(self):
        self.camera = picamera.PiCamera()
        self.camera.resolution = (WIDTH, HEIGHT)
        self.camera.framerate = FRAMERATE
    
    def capture_img_stream(self) -> BytesIO:
        img_stream = BytesIO()
        self.camera.capture(img_stream, format="jpeg")
        return img_stream
    
    def capture_image(self, path="PI_IMG.jpeg"):
        self.camera.capture(path, format="jpeg")
        
    def capture_video_stream(self) -> Generator:
        vid_stream = PiRGBArray(self.camera)
        for frame in self.camera.capture_continuous(vid_stream, format="bgr", use_video_port=True):
            yield frame
            # Clear buffer before next frame
            vid_stream.truncate(0)


class ImageProcessor:
    
    @staticmethod
    def load_img(img: Union[str, BytesIO, ndarray], resize=None) -> Image:
        if isinstance(img, str) or isinstance(img, BytesIO):
            image = Image.open(img).convert('1')
        elif isinstance(img, ndarray):
            image = Image.fromarray(img).convert('1')
        if resize:
            return image.resize(resize, Image.ANTIALIAS).convert('1')
        return image
    
    @staticmethod
    def convert_ppm(img: Union[str, BytesIO]):
        img = Image.open(img).resize((128, 64), Image.ANTIALIAS).convert('1')
        return img
    