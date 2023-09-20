import random
import numpy as np
from PIL import Image, ImageDraw
from pigui.ui import Component, EventListener
from pigui.utils.constants import *


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


class Block:
    def __init__(self, y, w, h):
        self.x = screen_width  # Outside of screen
        self.y = y
        self.w = w
        self.h = h
        self.is_collided = False

    def get_pos(self):
        return self.x, self.y, self.w, self.h


def player_block_collision(player, block):
    player_right = player.x + player.w
    player_bottom = player.y + player.h
    block_right = block.x + block.w
    block_bottom = block.y + block.h

    if (
        player.x < block_right
        and player_right > block.x
        and player.y < block_bottom
        and player_bottom > block.y
    ):
        return True
    return False


class Mario(Component):
    def __init__(self, document):
        super().__init__(document)
        self.score = 0
        self.speed = 1
        self.pixel_array = np.full(
            (screen_height, screen_width), game_bg_color, dtype=bool
        )
        self.player_is_jumping = False
        self.player = Player(59, 48, 10, 16)  # x, y, w, h
        self.register_event_listener(
            EventListener(
                [
                    (self.document.controller.joystick.on_up, self.player_jump),
                    (
                        self.document.controller.joystick.on_press,
                        self.print_block_player_state,
                    ),
                ],
                sleep=0.1,
                debounce=0.3,
            )
        )
        self.blocks_on_screen = set()

        self.is_paused = False

    def render(self):
        """Render current frame of the game"""
        if not self.is_paused:
            self.update_pixel()
        game = self.draw_player()
        game_img = Image.fromarray(game)
        self.collision_detection()
        self.draw_score(game_img)
        self.update_game_speed()
        return game_img

    def draw_score(self, image: Image):
        draw = ImageDraw.Draw(image)
        draw.text((70, 2), f"Score: {self.score}", font=font.resize(10), fill=255)

    def update_pixel(self):
        if random.random() > 0.98:
            block = self.gen_random_block()
            # TODO Check if overlap any other blocks
            self.blocks_on_screen.add(block)
        self.reset_pixel_array()  # Not the most efficient, but yeah
        self.draw_blocks()
        self.update_blocks_pos()

    def collision_detection(self):
        for b in self.blocks_on_screen:
            if not b.is_collided and player_block_collision(self.player, b):
                self.score += 1
                b.is_collided = True

    def reset_pixel_array(self):
        self.pixel_array = np.full(
            (screen_height, screen_width), game_bg_color, dtype=bool
        )

    def update_blocks_pos(self):
        for b in self.blocks_on_screen:
            b.x -= self.speed

    def gen_random_block(self) -> Block:
        y = random.randint(16, screen_height - game_block_min_h - 1)
        w = random.randint(game_block_min_w, game_block_max_w)
        h = random.randint(game_block_min_h, min(screen_height - y, game_block_max_h))
        return Block(y, w, h)

    def draw_blocks(self):
        blocks_to_remove = set()
        for b in self.blocks_on_screen:
            x, y, w, h = b.get_pos()
            if x + w < 0:
                blocks_to_remove.add(b)
                continue
            if 0 <= x <= screen_width:
                self.pixel_array[
                    y : y + h, x : min(x + w, screen_width - 1)
                ] = game_fg_color
        self.blocks_on_screen.difference_update(blocks_to_remove)

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

    def print_block_player_state(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            print("Game paused.")
            print("player", self.player.get_pos())
            print("blocks", [b.get_pos() for b in self.blocks_on_screen])
            print("n blocks", len([b.x < 128 for b in self.blocks_on_screen]))
        else:
            print("Game resumed.")

    def update_game_speed(self):
        self.speed = self.score // game_speed_divisor_score + 1
