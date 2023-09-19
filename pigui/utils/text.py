from typing import List
from pigui.utils.constants import *


def format_text(input_string: str, prev_line="") -> List[str]:
    """Function to format text for the display."""
    lines = []
    prev_line = prev_line

    for ix, word in enumerate(input_string.split()):
        cur_line = prev_line + " " + word
        if len(cur_line) <= text_line_width_char:
            prev_line = cur_line
        else:
            lines.append(prev_line.lstrip())
            prev_line = word

    if prev_line:
        lines.append(prev_line)
    return lines


def format_tokens(tokens: str, prev_line="") -> List[str]:
    """Function to format text, specifically, streaming tokens, which come in all sorts of formats for the display."""
    lines = []
    prev_line = prev_line

    tmp = (prev_line + tokens).lstrip()
    if len(tmp) <= text_line_width_char:
        return [tmp]

    if tokens.startswith(" "):
        prev_line += " "

    for ix, word in enumerate(tokens.split()):
        cur_line = prev_line + " " + word if ix > 0 else prev_line + word
        if len(cur_line) <= text_line_width_char:
            prev_line = cur_line
        else:
            lines.append(prev_line.lstrip())
            prev_line = word

    if prev_line:
        lines.append(prev_line)
    return lines
