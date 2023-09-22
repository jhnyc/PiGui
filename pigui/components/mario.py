import random
import numpy as np
from PIL import Image, ImageDraw
from pigui.ui import Component, EventListener
from pigui.utils.constants import *
from pigui.asset import mario_player, coin
from abc import ABC, abstractmethod


class Player:
    def __init__(self, x, y, w, h, player_array, jump_h=17):
        self.init_x = x
        self.init_y = y
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.player_array = player_array
        self.is_jumping = False
        self.is_ascending = False
        self.jump_h = jump_h
        assert self.player_array.shape == (self.h, self.w)

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

    def draw_on(self, image: np.ndarray) -> np.ndarray:
        """Draw player on top of an image."""
        new_image = np.copy(image)
        x, y, w, h = self.get_pos()
        new_image[y : y + h, x : x + w] += self.player_array
        return new_image


class Coin:
    def __init__(self, y, w, h, image=coin):
        self.x = screen_width  # Outside of screen
        self.y = y
        self.w = w
        self.h = h
        self.image = image
        self.is_collided = False
        assert self.image.shape == (self.h, self.w)

    def get_pos(self):
        return self.x, self.y, self.w, self.h

    def draw_on(self, image: np.ndarray):
        display_w = min(screen_width - self.x, self.w)
        image[self.y : self.y + self.h, self.x : self.x + display_w] = self.image[
            :, 0:display_w
        ]


def player_coin_collision(player, coin):
    player_right = player.x + player.w
    player_bottom = player.y + player.h
    coin_right = coin.x + coin.w
    coin_bottom = coin.y + coin.h

    if (
        player.x < coin_right
        and player_right > coin.x
        and player.y < coin_bottom
        and player_bottom > coin.y
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
        self.player = Player(59, 48, 10, 16, mario_player)  # x, y, w, h
        self.register_event_listener(
            EventListener(
                [
                    (self.document.controller.joystick.on_up, self.player_jump),
                    (
                        self.document.controller.joystick.on_press,
                        self.print_coin_player_state,
                    ),
                ],
                sleep=0.1,
                debounce=0.3,
            )
        )
        self.coins_on_screen = set()

        self.is_paused = False

    def render(self):
        """Render current frame of the game"""
        if not self.is_paused:
            self.update_pixel()
        game = self.player.draw_on(self.pixel_array)
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
            coin = self.gen_random_coin()
            # TODO Check if overlap any other coins
            self.coins_on_screen.add(coin)
        self.reset_pixel_array()  # Not the most efficient, but yeah
        self.draw_coins()
        self.update_coins_pos()

    def collision_detection(self):
        coins_to_remove = set()
        for b in self.coins_on_screen:
            if not b.is_collided and player_coin_collision(self.player, b):
                self.score += 1
                b.is_collided = True
                coins_to_remove.add(b)
        # After collision, remove the coin
        self.coins_on_screen.difference_update(coins_to_remove)

    def reset_pixel_array(self):
        self.pixel_array = np.full(
            (screen_height, screen_width), game_bg_color, dtype=bool
        )

    def update_coins_pos(self):
        for b in self.coins_on_screen:
            b.x -= self.speed

    def gen_random_coin(self) -> coin:
        y = random.randint(16, screen_height - game_coin_min_h - 1)
        w = random.randint(game_coin_min_w, game_coin_max_w)
        h = random.randint(game_coin_min_h, min(screen_height - y, game_coin_max_h))
        return Coin(y, w, h)

    def draw_coins(self):
        coins_to_remove = set()
        for b in self.coins_on_screen:
            x, y, w, h = b.get_pos()
            if x + w < 0:
                coins_to_remove.add(b)
                continue
            if 0 <= x <= screen_width:
                b.draw_on(self.pixel_array)
        self.coins_on_screen.difference_update(coins_to_remove)

    def player_jump(self):
        if self.player.is_jumping:
            return
        self.player.is_jumping = True
        self.player.is_ascending = True

    def print_coin_player_state(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            print("Game paused.")
            print("player", self.player.get_pos())
            print("coins", [b.get_pos() for b in self.coins_on_screen])
            print("n coins", len([b.x < 128 for b in self.coins_on_screen]))
        else:
            print("Game resumed.")

    def update_game_speed(self):
        self.speed = self.score // game_speed_divisor_score + 1
