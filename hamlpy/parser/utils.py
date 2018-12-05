from enum import Enum

from .core import Stream

DJANGO_TAG_OPEN = '{%'
DJANGO_TAG_CLOSE = '%}'
DJANGO_EXP_OPEN = '{{'
DJANGO_EXP_CLOSE = '}}'
HTML_CHARS = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}


class EscapeState(Enum):
    normal = 0
    in_tag = 1
    in_exp = 2


def html_escape(text):
    """
    Escapes HTML entities, matching substitutions used by the Ruby Haml library. Entities that occur inside Django tags
    or expressions are not escaped.
    """
    new_text = []
    state = EscapeState.normal
    stream = Stream(text)

    while stream.ptr < stream.length:
        ch = stream.text[stream.ptr]
        ch2 = stream.text[stream.ptr:stream.ptr + 2]

        if ch2 == DJANGO_TAG_OPEN or ch2 == DJANGO_EXP_OPEN:
            state = EscapeState.in_tag if ch2 == DJANGO_TAG_OPEN else EscapeState.in_exp
            stream.ptr += 2
            new_text.append(ch2)
        elif (state == EscapeState.in_tag and ch2 == DJANGO_TAG_CLOSE) \
                or (state == EscapeState.in_exp and ch2 == DJANGO_EXP_CLOSE):
            state = EscapeState.normal
            stream.ptr += 2
            new_text.append(ch2)
        else:
            stream.ptr += 1
            new_text.append(HTML_CHARS.get(ch, ch) if state == EscapeState.normal else ch)

    return ''.join(new_text)
