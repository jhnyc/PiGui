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

    def jump(self):
        if self.is_jumping:
            return
        self.is_jumping = True
        self.is_ascending = True


class ObjectCollection(ABC):
    def __init__(self):
        self.objects = set()

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self):
        pass


class CoinCollection(ObjectCollection):
    def __init__(self):
        super().__init__()
        self._collision_count = 0

    def generate(self):
        self.objects.add(Coin.generate())

    def update(self, player, speed):
        if random.random() > 0.98:
            self.generate()
        self.update_pos(speed)
        self.collision_detection(player)

    def update_pos(self, speed):
        for coin in self.objects:
            coin.x -= speed

    def collision_detection(self, player):
        coins_to_remove = set()
        for coin in self.objects:
            if coin.collision(player):
                self._collision_count += 1
                coins_to_remove.add(coin)
        self.objects.difference_update(coins_to_remove)

    def get_collision_count(self):
        return self._collision_count

    def draw(self, pixel_array):
        coins_to_remove = set()
        for coin in self.objects:
            x, y, w, h = coin.get_pos()
            if x + w < 0:
                coins_to_remove.add(coin)
                continue
            if 0 <= x <= screen_width:
                coin.draw_on(pixel_array)
        self.objects.difference_update(coins_to_remove)


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

    @staticmethod
    def generate():
        y = random.randint(16, screen_height - game_coin_min_h - 1)
        w = random.randint(game_coin_min_w, game_coin_max_w)
        h = random.randint(game_coin_min_h, min(screen_height - y, game_coin_max_h))
        return Coin(y, w, h)

    def collision(self, player):
        if self.is_collided:
            return False
        player_right = player.x + player.w
        player_bottom = player.y + player.h
        coin_right = self.x + self.w
        coin_bottom = self.y + self.h

        if (
            player.x < coin_right
            and player_right > self.x
            and player.y < coin_bottom
            and player_bottom > self.y
        ):
            self.is_collided = True
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
        self.player = Player(59, 48, 10, 16, mario_player)  # x, y, w, h
        self.register_event_listener(
            EventListener(
                [
                    (self.document.controller.joystick.on_up, self.player.jump),
                    (
                        self.document.controller.joystick.on_press,
                        self.pause_game,
                    ),
                ],
                sleep=0.1,
                debounce=0.3,
            )
        )
        self.coins = CoinCollection()
        self.is_paused = False

    def render(self):
        """Render current frame of the game"""
        self.reset_pixel_array()
        if not self.is_paused:
            self.coins.update(self.player, self.speed)
            self.coins.draw(self.pixel_array)
            self.score = self.coins.get_collision_count()
        # Draw player
        game = self.player.draw_on(self.pixel_array)
        game_img = Image.fromarray(game)

        self.draw_score(game_img)
        self.update_game_speed()
        return game_img

    def draw_score(self, image: Image):
        draw = ImageDraw.Draw(image)
        draw.text((70, 2), f"Score: {self.score}", font=font.resize(10), fill=255)

    def reset_pixel_array(self):
        self.pixel_array = np.full(
            (screen_height, screen_width), game_bg_color, dtype=bool
        )

    def pause_game(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            print("Game paused.")
        else:
            print("Game resumed.")

    def update_game_speed(self):
        self.speed = self.score // game_speed_divisor_score + 1
