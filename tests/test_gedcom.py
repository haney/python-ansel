#!/usr/bin/env python

"""Tests for `gedcom` package."""

import codecs

import pytest


def test_lookup(register):
    codec_info = codecs.lookup("gedcom")
    assert codec_info is not None
    assert "gedcom" == codec_info.name


@pytest.mark.parametrize(
    "input, expected",
    [
        (b"", ""),
        (b"abc", "abc"),
        pytest.param(
            b"P\xEAal",
            "Pa\u030Al",
            marks=pytest.mark.xfail(
                reason="Incremental reads not supported through stream interface"
            ),
        ),
        (b"\xBE", "\u25A1"),
        (b"\xBF", "\u25A0"),
        (b"\xCD", "\u0065"),
        (b"\xCE", "\u006F"),
        (b"\xCF", "\u00DF"),
    ],
)
def test_decode(register, fs, input, expected):
    fs.create_file("text.gedcom", contents=input)

    with codecs.open("text.gedcom", "r", encoding="gedcom") as reader:
        contents = []
        char = reader.read(1)
        while char:
            contents.append(char)
            char = reader.read(1)

    assert expected == "".join(contents)


@pytest.mark.parametrize(
    "input_parts, expected",
    [
        ([""], b""),
        (["abc"], b"abc"),
        (["Pa\u030Al"], b"P\xEAal"),
        (["P", "a\u030A", "l"], b"P\xEAal"),
        pytest.param(
            ["P", "a", "\u030A", "l"],
            b"P\xEAal",
            marks=pytest.mark.xfail(
                reason="Incremental writes not supported through stream interface"
            ),
        ),
        ("\u25A1", b"\xBE"),
        ("\u25A0", b"\xBF"),
        ("\u0065", b"\x65"),
        ("\u006F", b"\x6F"),
        ("\u00DF", b"\xCF"),
    ],
)
def test_encode(register, fs, input_parts, expected):
    with codecs.open("text.gedcom", "w", encoding="gedcom") as writer:
        for part in input_parts:
            writer.write(part)

    with codecs.open("text.gedcom", "rb") as reader:
        contents = reader.read()

    assert expected == contents
