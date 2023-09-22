import time
from abc import ABC, abstractmethod
from threading import Thread
from typing import Callable, Dict, List, Tuple, Union, Optional
from PIL import Image, ImageDraw, ImageFont
from pigui.hardware.controller import MasterController
from pigui.hardware.display import Display
from pigui.utils.constants import font


class State:
    def __init__(self, state=None):
        self.state = state

    def update(self, new_state):
        self.state = new_state


####################################################################################


class EventListener:
    def __init__(
        self,
        event_callback: List[Tuple[Union[bool, Callable], Callable]],
        sleep=0.1,
        debounce=None,
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
                    is_debounce = (
                        False
                        if not self.debounce_sec
                        else cur_time - self.debounce_times[ix] < self.debounce_sec
                    )
                    if is_debounce:
                        continue

                    callback()
                    # Update debounce_times
                    if self.debounce_sec:
                        self.debounce_times[ix] = cur_time
                time.sleep(self.sleep)

        thread = Thread(target=target)
        thread.start()

    def stop(self):
        self.stop_thread = True

    def on(self, func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result

        return wrapper


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
    def render(self) -> Optional[Image.Image]:
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

    def on(self, event, sleep=0.1, debounce=None):
        def decorator(func):
            self.register_event_listener(
                EventListener([(event, func)], sleep, debounce)
            )
            print(f"registered {event}, {func}")
            return func

        return decorator


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

    def render(self) -> Optional[Image.Image]:
        image = Image.new("1", (128, 64))

        # Control whether return a new Image or none
        is_empty = True

        # Layer components over one another
        for component in self.components:
            component_img = component.render()
            if component_img:
                image.paste(component_img, component.get_bounding_region())
                is_empty = False
        return image if not is_empty else None


####################################################################################


class Document:
    def __init__(self, width=128, height=64):
        self.displayer = Display()
        self.controller = MasterController()
        self.font = font

        self.components = []
        self.component_state = {}

        self.frames: Dict[str, Frame] = {}

        # Keep track of whether a frame's event listeners
        # e.g. if switch from Menu to an app, menu's event listener's would be stopped
        self.frame_event_listener_states: Dict[Frame, bool] = {}

        self.cur_frame_name = None

    def render(self):
        """Render document"""
        cur_frame = self.frames[self.cur_frame_name]
        self.start_frame_event_listeners(cur_frame)
        cur_frame_img = cur_frame.render()
        if cur_frame_img:
            self.displayer.display_img(cur_frame_img)

    def pack_frame(self, frame_name: str, frame: Frame):
        # Assume the first frame added as the entry point
        if frame_name in self.frames:
            raise ValueError(f"Frame `{frame_name}` already exists.")
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

    def start_frame_event_listeners(self, frame: Frame):
        if (
            frame not in self.frame_event_listener_states
            or self.frame_event_listener_states[frame] is False
        ):
            frame.start_event_listeners()
            self.frame_event_listener_states[frame] = True

    def remove_frame_event_listeners(self, frame: Frame):
        frame.stop_event_listeners()
        self.frame_event_listener_states[frame] = False

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
            time.sleep(0.03)


####################################################################################
