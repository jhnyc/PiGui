from PIL import Image, ImageDraw, ImageFont
from pigui.hardware.display import Display
from pigui.config import FONT
from abc import ABC, abstractmethod
from threading import Thread
import RPi.GPIO as GPIO
import time
from pigui.ui.helper import deep_compare
from typing import Tuple, List, Union, Callable


class State:
    def __init__(self, state=None):
        self.state = state

    def update(self, new_state):
        self.state = new_state


####################################################################################


class EventListener:
    # TODO maybe take (event, callback) tuple would be more ergonomic
    def __init__(
        self, events: List[Union[Callable, bool]], callbacks: List[Callable], sleep=0.1
    ):
        self.events = events
        self.callbacks = callbacks
        self.sleep = sleep
        self.stop_thread = False

    def start(self):
        self.stop_thread = False

        def target():
            while not self.stop_thread:
                for event, callback in zip(self.events, self.callbacks):
                    event_triggered = event if isinstance(event, bool) else event()
                    if event_triggered:
                        callback()
                time.sleep(self.sleep)

        thread = Thread(target=target)
        thread.start()

    def stop(self):
        self.stop_thread = True


####################################################################################


class Component(ABC):
    def __init__(self):
        self.event_listeners = []

    def get_states(self) -> dict:
        return {k: v.state for k, v in self.__dict__.items() if isinstance(v, State)}

    def get_bounding_region(self) -> Tuple[int, int, int, int]:
        return (0, 0, 128, 64)

    @abstractmethod
    def render(self) -> Image:
        pass

    # TODO component level event listener

    def add_event_listener(self, event_listener: EventListener):
        self.event_listeners.append(event_listener)


####################################################################################


class Frame(ABC):
    def __init__(self, components=None):
        self.components = []
        self.component_states = {}
        self.event_listeners: List[EventListener] = []

        if components:
            for comp in components:
                self.components.append(comp)
                self.component_states[comp] = comp.get_states()
                self.event_listeners.extend(comp.event_listeners)

    def pack(self, components: Union[Component, List[Component]]):
        if isinstance(components, Component):
            components = [components]
        for component in components:
            self.components.append(component)
            self.component_states[component] = component.get_states()
            self.event_listeners.extend(component.event_listeners)

    def start_event_listeners(self):
        for listener in self.event_listeners:
            listener.start()

    def stop_event_listeners(self):
        for listener in self.event_listeners:
            listener.stop()

    def render(self) -> Image:
        image = Image.new("1", (128, 64))
        # Layer components over one another
        for component in self.components:
            component_img = component.render()
            image.paste(component_img, component.get_bounding_region())
        return image


####################################################################################


class Document:
    def __init__(self, width=128, height=64):
        self.width = width
        self.height = height

        self.image = Image.new("1", (width, height))
        self.draw = ImageDraw.Draw(self.image)
        self.displayer = Display()
        self.font = FONT

        self.components = []
        self.component_state = {}

        self.frames: List[Frame] = []

        # A separate thread to check component states
        # TODO Thread(target=self.compare_state).start()

        # TODO need to start frame event listeners
        self.frame_event_listener_states = {}  # frame: bool

    def render(self):
        """Render document"""
        cur_frame = self.frames[-1]

        if (
            cur_frame not in self.frame_event_listener_states 
            or self.frame_event_listener_states[cur_frame] is False
        ):
            cur_frame.start_event_listeners()
            self.frame_event_listener_states[cur_frame] = True

        cur_frame_img = cur_frame.render()
        self.displayer.display_img(cur_frame_img)

    def add_frame(self, frame: Frame):
        self.frames.append(frame)

    def pack(self, component: Component):
        self.components.append(component)
        self.component_state.update({component: component.get_states()})

    def compare_state(self):
        while True:
            cur_state = {
                component: component.get_states() for component in self.components
            }
            if not deep_compare(cur_state, self.component_state):
                self.render()
                self.component_state = cur_state
            time.sleep(0.1)

    def main_loop(self):
        while True:
            self.render()
            time.sleep(0.1)


####################################################################################
