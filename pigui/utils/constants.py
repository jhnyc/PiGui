from PIL import ImageFont

# Text
text_left_padding = 5
text_line_width_char = 20
text_line_height_px = 15
text_lines = 4


class CustomFont(ImageFont.FreeTypeFont):
    """Wrapper class of ImageFont"""

    def resize(self, size) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(self.path, size)


font = CustomFont("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)


# Screen
screen_width = 128
screen_height = 64
screen_frame_rate = 30


# Game
game_bg_color = 0
game_fg_color = 1
game_speed_divisor_score = 10
game_block_min_h = 8
game_block_max_h = 8
game_block_min_w = 8
game_block_max_w = 8
