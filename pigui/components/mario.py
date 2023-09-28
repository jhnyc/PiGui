import random
import numpy as np
from PIL import Image, ImageDraw
from pigui.ui import Component, EventListener
from pigui.utils.constants import *
from pigui.asset import player, coin, block
from abc import ABC, abstractmethod
from enum import Enum, auto


class Player:
    def __init__(self, x, y, w, h, player_array, jump_h=18):
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
        self.is_landed_on_block = False
        self.block_y = None

    @property
    def bottom(self):
        return self.y + self.h

    def get_pos(self):
        return (self.x, self.y, self.w, self.h)

    def update(self):
        if self.is_jumping:
            self.y -= 1
            # if reach max height -> descend
            if self.init_y - self.y >= self.jump_h:
                self.is_jumping = False
            return
        if self.is_landed_on_block:
            self.y = self.block_y - self.h
            return
        if (
            not self.is_jumping
            and self.y != self.init_y
            and not self.is_landed_on_block
        ):
            self.y += 1
            return

    def draw_on(self, image: np.ndarray) -> np.ndarray:
        """Draw player on top of an image."""
        new_image = np.copy(image)
        x, y, w, h = self.get_pos()
        new_image[y : y + h, x : x + w] += self.player_array
        return new_image

    def jump(self):
        if self.is_jumping:
            return
        self.is_landed_on_block = False
        self.is_jumping = True
        self.is_ascending = True
        self.block_y = None

    def land_on_block(self, block):
        self.is_jumping = False
        self.is_landed_on_block = True
        self.block_y = block.y


class ObjectCollection(ABC):
    def __init__(self):
        self.objects = set()

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self):
        pass

    def update_pos(self, speed):
        for object in self.objects:
            object.x -= speed

    def generate_object(self, obj_type):
        self.objects.add(obj_type.generate())

    def draw(self, pixel_array):
        object_to_remove = set()
        for obj in self.objects:
            x, y, w, h = obj.get_pos()
            if x + w < 0:
                object_to_remove.add(obj)
                continue
            if 0 <= x <= screen_width:
                obj.draw_on(pixel_array)
        self.objects.difference_update(object_to_remove)

    @abstractmethod
    def reset(self):
        """Reset collection states"""


class CoinCollection(ObjectCollection):
    def __init__(self):
        super().__init__()
        self._collision_count = 0

    def update(self, player, speed):
        if random.random() > 0.98:
            self.generate_object(Coin)
        self.update_pos(speed)
        self.collision_detection(player)

    def collision_detection(self, player):
        coins_to_remove = set()
        for coin in self.objects:
            if coin.collision(player) != Collision.NONE:
                self._collision_count += 1
                coins_to_remove.add(coin)
        self.objects.difference_update(coins_to_remove)

    def get_collision_count(self):
        return self._collision_count

    def reset(self):
        self.objects.clear()
        self._collision_count = 0


class BlockCollection(ObjectCollection):
    def __init__(self):
        super().__init__()

    def update(self, speed):
        if random.random() > 0.99:
            self.generate_object(Block)
        self.update_pos(speed)

    def collision_detection(self, player) -> bool:
        for obj in self.objects:
            collision_type = obj.collision(player)
            # print(obj.get_pos(), collision_type, player.get_pos())
            if collision_type not in [Collision.NONE, Collision.BOTTOM]:
                return True
            if collision_type == Collision.BOTTOM:
                player.land_on_block(obj)
                return
        # No any type of collision, go back to ground
        player.is_landed_on_block = False
        return False

    def reset(self):
        self.objects.clear()


class Collision(Enum):
    """The side of the player that is collided with an object"""

    TOP = auto()
    BOTTOM = auto()
    LEFT = auto()
    RIGHT = auto()
    NONE = auto()


class GameObject(ABC):
    def __init__(self, y, w, h, image_array, x=screen_width):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.image_array = image_array
        assert self.image_array.shape == (self.h, self.w)

    def get_pos(self):
        return self.x, self.y, self.w, self.h

    def collision(self, player) -> Collision:
        player_right = player.x + player.w
        player_bottom = player.y + player.h
        object_right = self.x + self.w
        object_bottom = self.y + self.h

        self.is_collided = True
        #! Super spaghetti code here but it does the job for now
        if (
            0 <= player_bottom - self.y <= 2
            and player.y <= self.y
            and player_right >= self.x
            and player.x <= object_right
        ):
            return Collision.BOTTOM

        if (
            0 <= object_bottom - player.y <= 2
            and player_bottom >= self.y
            and player_right >= self.x
            and player.x <= object_right
        ):
            return Collision.TOP

        if (
            player.x <= object_right
            and player_right >= self.x
            and player.y <= object_bottom
            and player_bottom >= self.y
        ):
            return Collision.RIGHT

        if (
            player_right >= self.x
            and player.x <= self.x
            and player.y <= object_bottom
            and player_bottom >= self.y
        ):
            return Collision.LEFT

        self.is_collided = False
        return Collision.NONE

    def draw_on(self, image: np.ndarray):
        display_w = min(screen_width - self.x, self.w)
        image[self.y : self.y + self.h, self.x : self.x + display_w] = self.image_array[
            :, 0:display_w
        ]

    @classmethod
    def generate(cls):
        """Method to generate an object."""
        y = random.randint(16, screen_height - game_coin_min_h - 1)
        w = random.randint(game_coin_min_w, game_coin_max_w)
        h = random.randint(game_coin_min_h, min(screen_height - y, game_coin_max_h))
        return cls(y, w, h)


class Coin(GameObject):
    def __init__(self, y, w, h, image_array=coin):
        super().__init__(y, w, h, image_array)
        self.is_collided = False


class Block(GameObject):
    def __init__(self, y, w, h, image_array=block):
        super().__init__(y, w, h, image_array)
        self.is_collided = False


class Mario(Component):
    def __init__(self, document):
        super().__init__(document)
        self.score = 0
        self.speed = 1
        self.pixel_array = np.full(
            (screen_height, screen_width), game_bg_color, dtype=bool
        )
        self.player = Player(59, 48, 10, 16, player)  # x, y, w, h
        self.register_event_listener(
            EventListener(
                [
                    (self.document.controller.joystick.on_up, self.player.jump),
                    (
                        self.document.controller.joystick.on_press,
                        self.on_press,
                    ),
                ],
                sleep=0.1,
                debounce=0.3,
            )
        )
        self.coins = CoinCollection()
        self.blocks = BlockCollection()
        self.is_paused = False
        self.is_gameover = False

    def render(self):
        """Render current frame of the game"""
        self.reset_pixel_array()

        if self.is_paused or self.is_gameover:
            return
        self.blocks.update(self.speed)
        self.blocks.draw(self.pixel_array)
        self.player.update()
        if self.blocks.collision_detection(self.player):
            print("boom")
            self.is_gameover = True
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

    def reset_game(self):
        self.is_gameover = False
        self.score = 0
        self.speed = 1
        self.coins.reset()
        self.blocks.reset()

    def pause_game(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            print("Game paused.")
        else:
            print("Game resumed.")

    def on_press(self):
        if self.is_gameover:
            self.reset_game()
            return
        self.pause_game()

    def update_game_speed(self):
        self.speed = self.score // game_speed_divisor_score + 1
