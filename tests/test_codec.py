import pytest

import ansel.codec

from .conftest import EncodingError


class Codec(ansel.codec.Codec):
    name = "test"
    encode_char_map = {u"a": b"1", u"b": b"23", u"?": b"?"}
    decode_char_map = {b"a": u"1", b"b": u"23"}
    encode_modifier_map = {u"n": b"5", u"o": b"67"}
    decode_modifier_map = {b"n": u"5", b"o": u"67"}


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [(u"", b"", 0), (u"a", b"1", 1), (u"b", b"23", 1), (u"ab", b"123", 2)],
)
def test_encode_valid(input, expected, expected_len):
    codec = Codec()
    output, output_len = codec.encode(input)
    assert expected == output
    assert expected_len == output_len


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [
        (u"n", b"5", 1),
        (u"na", b"51", 2),
        (u"nb", b"523", 2),
        (u"an", b"51", 2),
        (u"aan", b"151", 3),
        (u"ano", b"6751", 3),
        (u"bon", b"56723", 3),
    ],
)
def test_encode_valid_with_modifiers(input, expected, expected_len):
    codec = Codec()
    output, output_len = codec.encode(input)
    assert expected == output
    assert expected_len == output_len


@pytest.mark.parametrize(
    "input, start, end, reason",
    [
        (u"+", 0, 1, "character maps to <undefined>"),
        (u"ab+", 2, 3, "character maps to <undefined>"),
    ],
)
def test_encode_invalid(input, start, end, reason):
    codec = Codec()
    with pytest.raises(UnicodeEncodeError) as exc_info:
        codec.encode(input)
    assert "test" == exc_info.value.encoding
    assert reason == exc_info.value.reason
    assert input == exc_info.value.object
    assert start == exc_info.value.start
    assert end == exc_info.value.end


@pytest.mark.parametrize("input", [u"+"])
def test_encode_invalid_raising_error_handler(error_handler, input):
    codec = Codec()
    with pytest.raises(EncodingError):
        codec.encode(input, errors="raises")


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [(u"+", b"?", 1), (u"a+b", b"1?23", 3), (u"a+n", b"15?", 3)],
)
def test_encode_invalid_with_replacement(input, expected, expected_len):
    codec = Codec()
    output, output_len = codec.encode(input, errors="replace")
    assert expected == output
    assert expected_len == output_len


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [(b"", u"", 0), (b"a", u"1", 1), (b"b", u"23", 1), (b"ab", u"123", 2)],
)
def test_decode_valid(input, expected, expected_len):
    codec = Codec()
    output, output_len = codec.decode(input)
    assert expected == output
    assert expected_len == output_len


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [
        (b"n", u"5", 1),
        (b"an", u"15", 2),
        (b"bn", u"235", 2),
        (b"na", u"15", 2),
        (b"naa", u"151", 3),
        (b"noa", u"1675", 3),
        (b"onb", u"23567", 3),
    ],
)
def test_decode_valid_with_modifiers(input, expected, expected_len):
    codec = Codec()
    output, output_len = codec.decode(input)
    assert expected == output
    assert expected_len == output_len


@pytest.mark.parametrize(
    "input, start, end, reason",
    [
        (b"+", 0, 1, "character maps to <undefined>"),
        (b"ab+", 2, 3, "character maps to <undefined>"),
    ],
)
def test_decode_invalid(input, start, end, reason):
    codec = Codec()
    with pytest.raises(UnicodeDecodeError) as exc_info:
        codec.decode(input)
    assert "test" == exc_info.value.encoding
    assert reason == exc_info.value.reason
    assert input == exc_info.value.object
    assert start == exc_info.value.start
    assert end == exc_info.value.end


@pytest.mark.parametrize("input", [b"+"])
def test_decode_invalid_raising_error_handler(error_handler, input):
    codec = Codec()
    with pytest.raises(EncodingError):
        codec.decode(input, errors="raises")


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [(b"+", u"\uFFFD", 1), (b"a+b", u"1\uFFFD23", 3), (b"an+", u"1\uFFFD5", 3)],
)
def test_decode_invalid_with_replacement(input, expected, expected_len):
    codec = Codec()
    output, output_len = codec.decode(input, errors="replace")
    assert expected == output
    assert expected_len == output_len
