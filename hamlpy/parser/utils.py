from __future__ import unicode_literals


def html_escape(s):
    """
    Escapes HTML entities, matching substitutions used the Ruby Haml library
    """
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    s = s.replace("'", "&#39;")
    return s
