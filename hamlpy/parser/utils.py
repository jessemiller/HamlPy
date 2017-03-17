from __future__ import unicode_literals

from .core import Stream

DJANGO_TAG_OPEN = '{%'
DJANGO_TAG_CLOSE = '%}'
DJANGO_EXP_OPEN = '{{'
DJANGO_EXP_CLOSE = '}}'
HTML_CHARS = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}


def html_escape(text):
    """
    Escapes HTML entities, matching substitutions used by the Ruby Haml library. Entities that occur inside Django tags
    or expressions are not escaped.
    """
    new_text = []
    state = 0  # 0 = normal, 1 = in tag, 2 = in expression

    stream = Stream(text)

    while stream.ptr < stream.length:
        ch = stream.text[stream.ptr]
        ch2 = stream.text[stream.ptr:stream.ptr + 2]

        if ch2 == DJANGO_TAG_OPEN or ch2 == DJANGO_EXP_OPEN:
            state = 1 if ch2 == DJANGO_TAG_OPEN else 2
            stream.ptr += 2
            new_text.append(ch2)
        elif (state == 1 and ch2 == DJANGO_TAG_CLOSE) or (state == 2 and ch2 == DJANGO_EXP_CLOSE):
            state = 0
            stream.ptr += 2
            new_text.append(ch2)
        else:
            stream.ptr += 1
            new_text.append(HTML_CHARS.get(ch, ch) if state == 0 else ch)

    return ''.join(new_text)
