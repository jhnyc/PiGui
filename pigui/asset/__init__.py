import numpy as np
from PIL import Image

player: np.ndarray = np.array(Image.open("pigui/asset/player.ppm"))
coin: np.ndarray = np.array(Image.open("pigui/asset/coin.ppm"))
block: np.ndarray = np.array(Image.open("pigui/asset/block.ppm"))
