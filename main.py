from pigui.ui.ui import Document, Frame
from pigui.components.stats import StatApp
import time

doc = Document()

stat = StatApp()

frame = Frame(components=[stat])


doc.add_frame(frame)
doc.main_loop()