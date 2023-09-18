from PIL import Image, ImageDraw, ImageFont
from pigui.hardware.display import Display
from pigui.hardware.controller import MasterController
from pigui.config import FONT
from abc import ABC, abstractmethod
from threading import Thread
import RPi.GPIO as GPIO
import time
from pigui.ui.helper import deep_compare
from typing import Tuple, List, Union, Callable, Dict, Tuple


class State:
    def __init__(self, state=None):
        self.state = state

    def update(self, new_state):
        self.state = new_state


####################################################################################


class EventListener:
    def __init__(
        self, event_callback: List[Tuple[Union[bool, Callable], Callable]], sleep=0.1, debounce=None
    ):
        self.event_callback = event_callback
        self.sleep = sleep
        
        self.stop_thread = False
        
        self.debounce_sec = debounce
        self.debounce_times = [0 for _ in self.event_callback] if debounce else None

    def start(self):
        self.stop_thread = False

        def target():
            while not self.stop_thread:
                for ix, (event, callback) in enumerate(self.event_callback):
                    event_triggered = event if isinstance(event, bool) else event()
                    if not event_triggered:
                        continue
                    # Event triggered -> check whether debounce or not
                    cur_time = time.time()
                    is_debounce = False if not self.debounce_sec else cur_time - self.debounce_times[ix] < self.debounce_sec
                    if is_debounce:
                        continue
                    
                    callback()
                    # Update debounce_times
                    if self.debounce_sec: self.debounce_times[ix] = cur_time
                time.sleep(self.sleep)

        thread = Thread(target=target)
        thread.start()

    def stop(self):
        self.stop_thread = True


####################################################################################


class Component(ABC):
    def __init__(self, document):
        self.document = document
        self.event_listeners = []

    def get_states(self) -> dict:
        return {k: v.state for k, v in self.__dict__.items() if isinstance(v, State)}

    def get_bounding_region(self) -> Tuple[int, int, int, int]:
        return (0, 0, 128, 64)

    @abstractmethod
    def render(self) -> Image:
        pass

    def register_event_listener(
        self, event_listener: Union[EventListener, List[EventListener]]
    ):
        if isinstance(event_listener, EventListener):
            self.event_listeners.append(event_listener)
        else:
            self.event_listeners.extend(event_listener)

    def as_frame(self, frame_name=None):
        frame = Frame(components=[self], frame_name=frame_name)
        return frame

    def goto_frame_fn(self, frame_name) -> Callable:
        def wrap():
            self.document.goto_frame(frame_name)

        return wrap


####################################################################################


class Frame(ABC):
    def __init__(self, components=None, frame_name=None):
        self.frame_name = frame_name
        self.components = []
        self.component_states = {}
        self.event_listeners: List[EventListener] = []

        if components:
            for comp in components:
                self.components.append(comp)
                self.component_states[comp] = comp.get_states()
                self.event_listeners.extend(comp.event_listeners)

    def pack_component(self, components: Union[Component, List[Component]]):
        if isinstance(components, Component):
            components = [components]
        for component in components:
            self.components.append(component)
            self.component_states[component] = component.get_states()
            self.event_listeners.extend(component.event_listeners)

    def start_event_listeners(self):
        print(f"{self.frame_name} EL Started", self.event_listeners)
        for listener in self.event_listeners:
            listener.start()

    def stop_event_listeners(self):
        print(f"{self.frame_name} EL Stopped", self.event_listeners)
        for listener in self.event_listeners:
            listener.stop()

    def render(self) -> Image:
        image = Image.new("1", (128, 64))
        # Layer components over one another
        for component in self.components:
            component_img = component.render()
            if component_img:
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
        self.controller = MasterController()
        self.font = FONT

        self.components = []
        self.component_state = {}

        self.frames: Dict[str, Frame] = {}

        # A separate thread to check component states
        # TODO Thread(target=self.compare_state).start()

        # TODO need to start frame event listeners
        self.frame_event_listener_states: Dict[Frame, bool] = {}

        self.cur_frame_name = None

    def render(self):
        """Render document"""
        cur_frame = self.frames[self.cur_frame_name]

        if (
            cur_frame not in self.frame_event_listener_states
            or self.frame_event_listener_states[cur_frame] is False
        ):
            cur_frame.start_event_listeners()
            self.frame_event_listener_states[cur_frame] = True

        cur_frame_img = cur_frame.render()
        if cur_frame_img:
            self.displayer.display_img(cur_frame_img)

    def pack_frame(self, frame_name: str, frame: Frame):
        # Assume the first frame added as the entry point
        if self.cur_frame_name is None:
            self.cur_frame_name = frame_name
        self.frames[frame_name] = frame

    def goto_frame(self, frame_name):
        # Before rendering new frame, remove current frame event listeners
        cur_frame = self.frames[self.cur_frame_name]
        self.remove_frame_event_listeners(cur_frame)

        if frame_name not in self.frames:
            raise ValueError(f"Frame `{frame_name}` not found.")
        self.cur_frame_name = frame_name

    def remove_frame_event_listeners(self, frame: Frame):
        frame.stop_event_listeners()
        self.frame_event_listener_states[frame] = False

    def compare_state(self):
        while True:
            cur_state = {
                component: component.get_states() for component in self.components
            }
            if not deep_compare(cur_state, self.component_state):
                self.render()
                self.component_state = cur_state
            time.sleep(0.1)

    def main_loop(self, fps: bool = True):
        if fps:
            frames = 0
            start_time = time.time()

        while True:
            self.render()
            if not fps:
                continue
            frames += 1
            elapsed_time = time.time() - start_time
            if elapsed_time >= 1.0:
                fps = frames / elapsed_time
                print(f"FPS: {fps:.2f}")
                frames = 0
                start_time = time.time()


####################################################################################
