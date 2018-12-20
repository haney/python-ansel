# -*- coding: utf-8 -*-

"""Top-level package for ANSEL Codecs."""

__author__ = """David Haney"""
__email__ = "david.haney@gmail.com"
__version__ = "0.1.0"

import ansel.encodings.ansel
import codecs


def register():
    def encoding_lookup(name):
        if name == "ansel":
            return ansel.encodings.ansel.getregentry()
        return None

    codecs.register(encoding_lookup)
