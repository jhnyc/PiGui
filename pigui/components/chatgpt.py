from typing import List
from PIL import Image, ImageDraw
from pigui.components.api.chatgpt import stream_chat_completion
from pigui.ui import Component, Document, EventListener
from pigui.utils.constants import *
from pigui.utils.text import format_text, format_tokens


class ChatGPT(Component):
    def __init__(self, document: Document):
        super().__init__(document)
        self.display_text = ""
        self.display_text_chunks = format_text(self.display_text)
        self.register_event_listener(
            [
                EventListener([(True, self.update_display_text)], sleep=0.2),
                EventListener(
                    [
                        (self.document.controller.joystick.on_up, self.on_scroll_up),
                        (
                            self.document.controller.joystick.on_right,
                            self.on_scroll_down,
                        ),
                        (
                            self.document.controller.joystick.on_press,
                            self.update_prompt,
                        ),
                    ],
                    sleep=0.1,
                ),
            ],
        )
        self.prompt = "What is python?"
        self.response_token_stream = stream_chat_completion(self.prompt)
        self.is_streaming = True
        self.line_pos = 0

    def render(self):
        image = Image.new("1", (128, 64))
        draw = ImageDraw.Draw(image)

        for ix, line in enumerate(
            self.display_text_chunks[self.line_pos : self.line_pos + text_lines]
        ):
            draw.text((0, ix * text_line_height_px), line, fill=255)

        return image

    def update_display_text(self):
        if not self.is_streaming:
            return
        try:
            new_text = next(self.response_token_stream)
            prev_line = self.display_text_chunks[-1] if self.display_text_chunks else ""
            lines = format_tokens(new_text, prev_line)

            # Remove last chunk since we started with it
            if self.display_text_chunks:
                self.display_text_chunks.pop()

            self.display_text_chunks += lines
        except StopIteration:
            self.is_streaming = False

    def on_scroll_up(self):
        self.line_pos = max(0, self.line_pos - 1)

    def on_scroll_down(self):
        self.line_pos = min(len(self.display_text_chunks) - 4, self.line_pos + 1)

    def update_prompt(self):
        self.prompt = "Explain quantum physics like I'm 5"
        self.response_token_stream = stream_chat_completion(self.prompt)
        self.is_streaming = True
