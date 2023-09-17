from pigui.ui.ui import Document, Frame
from pigui.components.stats import StatApp
from pigui.components.menu import Menu
from pigui.hardware.controller import Button, Joystick
import time

doc = Document()

stat_frame = StatApp(doc).as_frame()
menu = Menu(doc)

menu_frame = Frame(components=[menu])


doc.pack_frame("menu", menu_frame)
doc.pack_frame("stat", stat_frame)
doc.main_loop()