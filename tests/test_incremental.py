import pytest

import ansel.incremental

from .conftest import EncodingError


class IncrementalDecoder(ansel.incremental.IncrementalDecoder):
    name = "test"
    encode_char_map = {"a": b"1", "b": b"23", "?": b"?"}
    decode_char_map = {ord(b"a"): "1", ord(b"b"): "23"}
    encode_modifier_map = {"n": b"5", "o": b"67"}
    decode_modifier_map = {ord(b"n"): "5", ord(b"o"): "67"}
    decode_control_map = {ord(b"\n"): "8", ord(b"\t"): "9A"}


class IncrementalEncoder(ansel.incremental.IncrementalEncoder):
    name = "test"
    encode_char_map = {"a": b"1", "b": b"23", "?": b"?"}
    decode_char_map = {ord(b"a"): "1", ord(b"b"): "23"}
    encode_modifier_map = {"n": b"5", "o": b"67"}
    decode_modifier_map = {ord(b"n"): "5", ord(b"o"): "67"}


@pytest.mark.parametrize(
    "input, state",
    [
        ("", 0),
        ("a", 0x131),
        ("ab", 0x13233),
        ("n", 0x135),
        ("ao", 0x1363731),
        ("annn", 0x135353531),
        ("annnb", 0x13233),
    ],
)
def test_encode_getstate(input, state):
    encoder = IncrementalEncoder()
    encoder.encode(input)
    assert state == encoder.getstate()


@pytest.mark.parametrize(
    "state, input, expected",
    [
        (0, "a", b"1"),
        (0x131, "b", b"123"),
        (0x131, "nb", b"5123"),
        (0x1353531, "nb", b"555123"),
    ],
)
def test_encode_setstate(state, input, expected):
    encoder = IncrementalEncoder()
    encoder.setstate(state)
    assert state == encoder.getstate()
    output = encoder.encode(input, final=True)
    assert expected == output
    assert 0 == encoder.getstate()


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [("", b"", 0), ("a", b"1", 1), ("b", b"23", 1), ("ab", b"123", 2)],
)
def test_encode_valid(input, expected, expected_len):
    encoder = IncrementalEncoder()
    output = encoder.encode(input, final=True)
    assert expected == output
    assert 0 == encoder.getstate()


@pytest.mark.parametrize(
    "partials",
    [
        ["a"],
        ["a", "b"],
        ["ab", ""],
        ["a", "nb"],
        ["an", "nb"],
        ["a", "n", "n", "b"],
        ["n", "o"],
    ],
)
def test_encode_incremental(partials):
    encoder = IncrementalEncoder()
    expected = encoder.encode("".join(partials), final=True)
    actual = b"".join(encoder.encode(partial) for partial in partials[0:-1])
    actual += encoder.encode(partials[-1], final=True)
    assert expected == actual


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
    encoder = IncrementalEncoder()
    output = encoder.encode(input, final=True)
    assert expected == output
    assert 0 == encoder.getstate()


@pytest.mark.parametrize(
    "input, start, end, reason",
    [
        ("+", 0, 1, "character maps to <undefined>"),
        ("ab+", 2, 3, "character maps to <undefined>"),
    ],
)
def test_encode_invalid(input, start, end, reason):
    encoder = IncrementalEncoder()
    with pytest.raises(UnicodeEncodeError) as exc_info:
        encoder.encode(input, final=True)
    assert "test" == exc_info.value.encoding
    assert reason == exc_info.value.reason
    assert input == exc_info.value.object
    assert start == exc_info.value.start
    assert end == exc_info.value.end
    assert 0 == encoder.getstate()


@pytest.mark.parametrize("input", ["+"])
def test_encode_invalid_raising_error_handler(error_handler, input):
    encoder = IncrementalEncoder(errors="raises")
    with pytest.raises(EncodingError):
        encoder.encode(input, final=True)
    assert 0 == encoder.getstate()


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [("+", b"?", 1), ("a+b", b"1?23", 3), ("a+n", b"15?", 3)],
)
def test_encode_invalid_with_replacement(input, expected, expected_len):
    encoder = IncrementalEncoder(errors="replace")
    output = encoder.encode(input, final=True)
    assert expected == output
    assert 0 == encoder.getstate()


@pytest.mark.parametrize(
    "input, state",
    [
        (b"", (b"", 0)),
        (b"a", (b"", 0)),
        (b"n", (b"", 0x1000035)),
        (b"no", (b"", 0x1000036000037000035)),
        (b"nob", (b"", 0)),
        (b"ano", (b"", 0x1000036000037000035)),
    ],
)
def test_decode_getstate(input, state):
    decoder = IncrementalDecoder()
    decoder.decode(input)
    assert state == decoder.getstate()


@pytest.mark.parametrize(
    "state, input, expected",
    [
        ((b"", 0), b"", ""),
        ((b"", 0x1000035), b"a", "15"),
        ((b"", 0x1000035), b"na", "155"),
        ((b"", 0x1000036000037), b"na", "1567"),
    ],
)
def test_decode_setstate(state, input, expected):
    decoder = IncrementalDecoder()
    decoder.setstate(state)
    assert state == decoder.getstate()
    output = decoder.decode(input, final=True)
    assert expected == output
    assert (b"", 0) == decoder.getstate()


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [(b"", "", 0), (b"a", "1", 1), (b"b", "23", 1), (b"ab", "123", 2)],
)
def test_decode_valid(input, expected, expected_len):
    decoder = IncrementalDecoder()
    output = decoder.decode(input)
    assert expected == output
    assert (b"", 0) == decoder.getstate()


@pytest.mark.parametrize(
    "partials",
    [
        [b"a"],
        [b"a", b"b"],
        [b"ab", b""],
        [b"an", b"b"],
        [b"an", b"nb"],
        [b"a", b"n", b"n", b"b"],
        [b"n", b"o"],
        [b"a", b"n", b"\n"],
        [b"b", b"o", b"\t", b"a"],
    ],
)
def test_decode_incremental(partials):
    decoder = IncrementalDecoder()
    expected = decoder.decode(b"".join(partials), final=True)
    actual = "".join(decoder.decode(partial) for partial in partials[0:-1])
    actual += decoder.decode(partials[-1], final=True)
    assert expected == actual


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
    decoder = IncrementalDecoder()
    output = decoder.decode(input, final=True)
    assert expected == output
    assert (b"", 0) == decoder.getstate()


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [(b"\n", "8", 1), (b"\t", "9A", 1), (b"\n\t", "89A", 2)],
)
def test_decode_valid_with_control(input, expected, expected_len):
    decoder = IncrementalDecoder()
    output = decoder.decode(input)
    assert expected == output
    assert (b"", 0) == decoder.getstate()


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
def test_decode_valid_with_control_modifiers(input, expected, expected_len):
    decoder = IncrementalDecoder()
    output = decoder.decode(input, final=True)
    assert expected == output
    assert (b"", 0) == decoder.getstate()


@pytest.mark.parametrize(
    "input, start, end, reason",
    [
        (b"+", 0, 1, "character maps to <undefined>"),
        (b"ab+", 2, 3, "character maps to <undefined>"),
    ],
)
def test_decode_invalid(input, start, end, reason):
    decoder = IncrementalDecoder()
    with pytest.raises(UnicodeDecodeError) as exc_info:
        decoder.decode(input)
    assert "test" == exc_info.value.encoding
    assert reason == exc_info.value.reason
    assert input == exc_info.value.object
    assert start == exc_info.value.start
    assert end == exc_info.value.end
    assert (b"", 0) == decoder.getstate()


@pytest.mark.parametrize("input", [b"+"])
def test_decode_invalid_raising_error_handler(input):
    decoder = IncrementalDecoder(errors="raises")
    with pytest.raises(EncodingError):
        decoder.decode(input)
    assert (b"", 0) == decoder.getstate()


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [(b"+", "\uFFFD", 1), (b"a+b", "1\uFFFD23", 3), (b"an+", "1\uFFFD5", 3)],
)
def test_decode_invalid_with_replacement(input, expected, expected_len):
    decoder = IncrementalDecoder(errors="replace")
    output = decoder.decode(input)
    assert expected == output
    assert (b"", 0) == decoder.getstate()
