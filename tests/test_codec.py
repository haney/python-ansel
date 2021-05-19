import pytest

import ansel.codec

from .conftest import EncodingError


class Codec(ansel.codec.Codec):
    name = "test"
    encode_char_map = {"a": b"1", "b": b"23", "?": b"?"}
    decode_char_map = {ord(b"a"): "1", ord(b"b"): "23"}
    encode_modifier_map = {"n": b"5", "o": b"67"}
    decode_modifier_map = {ord(b"n"): "5", ord(b"o"): "67"}
    decode_control_map = {ord(b"\n"): "8", ord(b"\t"): "9A"}


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [("", b"", 0), ("a", b"1", 1), ("b", b"23", 1), ("ab", b"123", 2)],
)
def test_encode_valid(input, expected, expected_len):
    codec = Codec()
    output, output_len = codec.encode(input)
    assert expected == output
    assert expected_len == output_len


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [
        ("n", b"5", 1),
        ("na", b"51", 2),
        ("nb", b"523", 2),
        ("an", b"51", 2),
        ("aan", b"151", 3),
        ("ano", b"6751", 3),
        ("bon", b"56723", 3),
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
        ("+", 0, 1, "character maps to <undefined>"),
        ("ab+", 2, 3, "character maps to <undefined>"),
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


@pytest.mark.parametrize("input", ["+"])
def test_encode_invalid_raising_error_handler(error_handler, input):
    codec = Codec()
    with pytest.raises(EncodingError):
        codec.encode(input, errors="raises")


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [("+", b"?", 1), ("a+b", b"1?23", 3), ("a+n", b"15?", 3)],
)
def test_encode_invalid_with_replacement(input, expected, expected_len):
    codec = Codec()
    output, output_len = codec.encode(input, errors="replace")
    assert expected == output
    assert expected_len == output_len


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [(b"", "", 0), (b"a", "1", 1), (b"b", "23", 1), (b"ab", "123", 2)],
)
def test_decode_valid(input, expected, expected_len):
    codec = Codec()
    output, output_len = codec.decode(input)
    assert expected == output
    assert expected_len == output_len


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [
        (b"n", " 5", 1),
        (b"an", "1 5", 2),
        (b"bn", "23 5", 2),
        (b"na", "15", 2),
        (b"naa", "151", 3),
        (b"noa", "1675", 3),
        (b"onb", "23567", 3),
    ],
)
def test_decode_valid_with_modifiers(input, expected, expected_len):
    codec = Codec()
    output, output_len = codec.decode(input)
    assert expected == output
    assert expected_len == output_len


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [(b"\n", "8", 1), (b"\t", "9A", 1), (b"\n\t", "89A", 2)],
)
def test_decode_valid_with_control(input, expected, expected_len):
    codec = Codec()
    output, output_len = codec.decode(input)
    assert expected == output
    assert expected_len == output_len


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [
        (b"n", " 5", 1),
        (b"\nn", "8 5", 2),
        (b"\tn", "9A 5", 2),
        (b"n\n", " 58", 2),
        (b"n\n\n", " 588", 3),
        (b"no\n", " 6758", 3),
        (b"on\t", " 5679A", 3),
    ],
)
def test_decode_valid_with_control_and_modifiers(input, expected, expected_len):
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
    [(b"+", "\uFFFD", 1), (b"a+b", "1\uFFFD23", 3), (b"an+", "1\uFFFD5", 3)],
)
def test_decode_invalid_with_replacement(input, expected, expected_len):
    codec = Codec()
    output, output_len = codec.decode(input, errors="replace")
    assert expected == output
    assert expected_len == output_len
