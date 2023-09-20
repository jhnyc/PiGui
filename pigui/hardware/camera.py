from io import BytesIO
from typing import Generator, Union
import picamera
from numpy import ndarray
from picamera.array import PiRGBArray
from PIL import Image
from pigui.utils.constants import *


class Camera:
    def __init__(self, image_resolution=(1920, 1080)):
        self.camera = picamera.PiCamera()
        self.camera.resolution = (screen_width, screen_height)
        self.image_resolution = image_resolution
        self.camera.framerate = screen_frame_rate

    def capture_img_stream(self, format="jpeg") -> BytesIO:
        img_stream = BytesIO()
        self.camera.capture(img_stream, format=format)
        return img_stream

    def capture_image(self, path="PI_IMG.jpeg", format="jpeg"):
        # Update camera resolution when taking photo
        self.camera.resolution = self.image_resolution
        self.camera.capture(path, format=format)
        # Revert camera resolution optimized for video/preview mode when done
        self.camera.resolution = (screen_width, screen_height)

    def video_stream(self, format="bgr") -> Generator:
        vid_stream = PiRGBArray(self.camera)
        for frame in self.camera.capture_continuous(
            vid_stream, format=format, use_video_port=True
        ):
            yield frame
            # Clear buffer before next frame
            vid_stream.truncate(0)

    def close(self):
        self.camera.close()


class ImageProcessor:
    @staticmethod
    def load_img(img: Union[str, BytesIO, ndarray], resize=None) -> Image:
        if isinstance(img, str) or isinstance(img, BytesIO):
            image = Image.open(img).convert("1")
        elif isinstance(img, ndarray):
            image = Image.fromarray(img).convert("1")
        if resize:
            return image.resize(resize, Image.ANTIALIAS).convert("1")
        return image

    @staticmethod
    def convert_ppm(img: Union[str, BytesIO]):
        img = Image.open(img).resize((128, 64), Image.ANTIALIAS).convert("1")
        return img
