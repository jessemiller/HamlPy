from __future__ import unicode_literals


DJANGO_TAG_OPEN = '{%'
DJANGO_TAG_CLOSE = '%}'
HTML_CHARS = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}


def html_escape(text):
    """
    Escapes HTML entities, matching substitutions used the Ruby Haml library. Entities that occur inside Django tags
    are not escaped.
    """
    new_text = []
    in_django_tag = False

    for index, ch in enumerate(text):
        ch2 = text[index:index+2]

        if ch2 == DJANGO_TAG_OPEN:
            in_django_tag = True

        if in_django_tag:
            if ch2 == DJANGO_TAG_CLOSE:
                in_django_tag = False
            sub = ch
        else:
            sub = HTML_CHARS.get(ch) or ch

        new_text.append(sub)

    return ''.join(new_text)
