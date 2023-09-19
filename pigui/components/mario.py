from PIL import Image
from pigui.ui.ui import Component, EventListener
import numpy as np
from pigui.utils.constants import *
import random
from collections import namedtuple
import copy


class Player:
    def __init__(self, x, y, w, h, jump_h=17):
        self.init_x = x
        self.init_y = y
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.is_jumping = False
        self.is_ascending = False
        self.jump_h = jump_h

    def get_pos(self):
        if self.is_jumping:
            self.y += -1 if self.is_ascending else 1
            # if reach max height -> descend
            if self.init_y - self.y >= self.jump_h:
                self.is_ascending = False
            # if reach ground -> no longer jumping
            if self.init_y == self.y:
                self.is_jumping = False
        return (self.x, self.y, self.w, self.h)


class Mario(Component):
    def __init__(self, document, speed=1):
        super().__init__(document)
        self.speed = speed
        self.pixel_array = np.full(
            (screen_height, screen_width), game_bg_color, dtype=bool
        )
        self.player_is_jumping = False
        self.player = Player(59, 48, 10, 16)  # x, y, w, h
        # objects: blocks, coins, player
        self.register_event_listener(
            EventListener(
                [(self.document.controller.joystick.on_up, self.player_jump)],
                debounce=0.5,
            )
        )

    def render(self):
        """Render current frame of the game"""
        self.update_pixel()
        game = self.draw_player()
        return Image.fromarray(game)

    def update_pixel(self):
        if random.random() > 0.99:
            x, y, w, h = self.gen_random_xywh()
            while self.has_existing_block(x, y, w, h):
                x, y, w, h = self.gen_random_xywh()
            self.draw_blocks(x, y, w, h)
        self.pixel_array = np.roll(self.pixel_array, -self.speed, axis=1)
        self.pixel_array[:, -self.speed :] = game_bg_color

    def gen_random_xywh(self):
        x = random.randint(10, screen_width - 1)
        y = random.randint(0, screen_height - 20)
        w = random.randint(0, screen_width - x)
        h = random.randint(0, screen_height - 20 - y)
        return x, y, w, h

    def has_existing_block(self, x, y, w, h):
        return self.pixel_array[y : y + h, x : x + w].any()

    def draw_blocks(self, x, y, width, height):
        self.pixel_array[y : y + height, x : x + width] = game_fg_color

    def draw_player(self) -> np.ndarray:
        """Draw player on top of moving background."""
        background = np.copy(self.pixel_array)
        x, y, w, h = self.player.get_pos()
        background[y : y + h, x : x + w] = game_fg_color
        return background

    def player_jump(self):
        if self.player.is_jumping:
            return
        self.player.is_jumping = True
        self.player.is_ascending = True
