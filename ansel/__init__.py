"""Top-level package for ANSEL Codecs."""

__author__ = """David Haney"""
__email__ = "david.haney@gmail.com"
__version__ = "1.0.0"


import codecs

from .encodings import ansel, gedcom


def register():
    def encoding_lookup(name):
        if name == "ansel":
            return ansel.getregentry()
        elif name == "gedcom":
            return gedcom.getregentry()
        return None

    codecs.register(encoding_lookup)
