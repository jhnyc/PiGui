import time
from abc import ABC, abstractmethod
from threading import Thread
from typing import Callable, List, Union
import RPi.GPIO as GPIO


# TODO - add debounce mechanism
class Controller(ABC):
    """Individual controller such as button, joystick, etc."""

    def __init__(self):
        self.event_types = {}  # `event`: func() -> bool

    def set_event_listener(
        self, type: str, callback: Callable, criteria: Union[str, Callable]
    ):
        if type not in self.event_types:
            raise ValueError("Invalid event type.")

        if not callable(criteria) and criteria not in ["once", "infinite"]:
            raise ValueError("Invalid criteria.")

        event_listen_fn = self.event_types[type]

        def event_listener():
            while True:
                # Event not triggered -> continue listening
                if not event_listen_fn():
                    time.sleep(0.1)
                    continue
                # Event triggered
                callback()
                # TODO refactor this ugly monstrosity
                if criteria == "once":
                    break
                if callable(criteria) and criteria():
                    break

        thread = Thread(target=event_listener)
        thread.start()


class Joystick(Controller):
    def __init__(self, gpio_x_pin, gpio_y_pin, gpio_z_pin):
        GPIO.setmode(GPIO.BCM)
        self.gpio_x_pin = gpio_x_pin
        self.gpio_y_pin = gpio_y_pin
        self.gpio_z_pin = gpio_z_pin
        GPIO.setup([gpio_x_pin, gpio_y_pin], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(gpio_z_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.event_types = {
            "on_press": self.on_press,
            "on_up": self.on_up,
            "on_right": self.on_right,
        }

    def on_press(self):
        if GPIO.input(self.gpio_z_pin) == 0:
            return True
        return False

    def on_up(self):
        if GPIO.input(self.gpio_y_pin) == 0:
            return True
        return False

    def on_right(self):
        if GPIO.input(self.gpio_x_pin) == 0:
            return True
        return False


class Button(Controller):
    def __init__(self, gpio_pin: int):
        self.gpio_pin = gpio_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.event_types = {"on_press": self.on_press}

    def on_press(self):
        if GPIO.input(self.gpio_pin) == 0:
            return True
        return False


# TODO this interface kind of weird
class MasterController:
    """Interface for all controller/input devices."""

    def __init__(self):
        self.joystick = Joystick(27, 17, 22)
        self.button = Button(4)

    def on_up(self):
        self.joystick.on_up()

    def on_down(self):
        self.joystick.on_up()

    def on_left(self):
        self.joystick.on_right()

    def on_right(self):
        self.joystick.on_right()

    def on_press(self):
        self.joystick.on_press()
