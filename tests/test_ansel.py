#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ansel` package."""

import codecs

import pytest


def test_lookup(register):
    codec_info = codecs.lookup("ansel")
    assert codec_info is not None
    assert "ansel" == codec_info.name


@pytest.mark.parametrize(
    "input, expected",
    [
        (b"", u""),
        (b"abc", u"abc"),
        pytest.param(
            b"P\xEAal",
            u"Pa\u030Al",
            marks=pytest.mark.xfail(
                reason="Incremental reads not supported through stream interface"
            ),
        ),
    ],
)
def test_decode(register, fs, input, expected):
    fs.create_file("text.ansel", contents=input)

    with codecs.open("text.ansel", "r", encoding="ansel") as reader:
        contents = []
        char = reader.read(1)
        while char:
            contents.append(char)
            char = reader.read(1)

    assert expected == "".join(contents)


@pytest.mark.parametrize(
    "input_parts, expected",
    [
        ([u""], b""),
        ([u"abc"], b"abc"),
        ([u"Pa\u030Al"], b"P\xEAal"),
        ([u"P", u"a\u030A", u"l"], b"P\xEAal"),
        pytest.param(
            [u"P", u"a", u"\u030A", u"l"],
            b"P\xEAal",
            marks=pytest.mark.xfail(
                reason="Incremental writes not supported through stream interface"
            ),
        ),
    ],
)
def test_encode(register, fs, input_parts, expected):
    with codecs.open("text.ansel", "w", encoding="ansel") as writer:
        for part in input_parts:
            writer.write(part)

    with codecs.open("text.ansel", "rb") as reader:
        contents = reader.read()

    assert expected == contents
