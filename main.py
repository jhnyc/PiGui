from pigui.ui.ui import Document, Frame
from pigui.components.stats import StatApp
from pigui.components.menu import Menu
from pigui.components.camera import CameraApp
from pigui.hardware.controller import Button, Joystick
import time

doc = Document()

stat_frame = StatApp(doc).as_frame("stat")
cam_frame = CameraApp(doc).as_frame("cam")
menu = Menu(doc)

menu_frame = Frame(components=[menu], frame_name="menu")


doc.pack_frame("menu", menu_frame)
doc.pack_frame("stat", stat_frame)
doc.pack_frame("camera", cam_frame)
doc.main_loop(fps=False)
