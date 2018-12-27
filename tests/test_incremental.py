import pytest

import ansel.incremental

from .conftest import EncodingError


class IncrementalDecoder(ansel.incremental.IncrementalDecoder):
    name = "test"
    encode_char_map = {u"a": b"1", "b": b"23", u"?": b"?"}
    decode_char_map = {b"a": u"1", b"b": u"23"}
    encode_modifier_map = {u"n": b"5", u"o": b"67"}
    decode_modifier_map = {b"n": u"5", b"o": u"67"}


class IncrementalEncoder(ansel.incremental.IncrementalEncoder):
    name = "test"
    encode_char_map = {u"a": b"1", u"b": b"23", u"?": b"?"}
    decode_char_map = {b"a": u"1", b"b": u"23"}
    encode_modifier_map = {u"n": b"5", u"o": b"67"}
    decode_modifier_map = {b"n": u"5", b"o": u"67"}


@pytest.mark.parametrize(
    "input, state",
    [
        (u"", 0),
        (u"a", 0x131),
        (u"ab", 0x13233),
        (u"n", 0x135),
        (u"ao", 0x1363731),
        (u"annn", 0x135353531),
        (u"annnb", 0x13233),
    ],
)
def test_encode_getstate(input, state):
    encoder = IncrementalEncoder()
    encoder.encode(input)
    assert state == encoder.getstate()


@pytest.mark.parametrize(
    "state, input, expected",
    [
        (0, u"a", b"1"),
        (0x131, u"b", b"123"),
        (0x131, u"nb", b"5123"),
        (0x1353531, u"nb", b"555123"),
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
    [(u"", b"", 0), (u"a", b"1", 1), (u"b", b"23", 1), (u"ab", b"123", 2)],
)
def test_encode_valid(input, expected, expected_len):
    encoder = IncrementalEncoder()
    output = encoder.encode(input, final=True)
    assert expected == output
    assert 0 == encoder.getstate()


@pytest.mark.parametrize(
    "partials",
    [
        [u"a"],
        [u"a", u"b"],
        [u"ab", u""],
        [u"a", u"nb"],
        [u"an", u"nb"],
        [u"a", u"n", u"n", u"b"],
        [u"n", u"o"],
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
    encoder = IncrementalEncoder()
    output = encoder.encode(input, final=True)
    assert expected == output
    assert 0 == encoder.getstate()


@pytest.mark.parametrize(
    "input, start, end, reason",
    [
        (u"+", 0, 1, "character maps to <undefined>"),
        (u"ab+", 2, 3, "character maps to <undefined>"),
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


@pytest.mark.parametrize("input", [u"+"])
def test_encode_invalid_raising_error_handler(error_handler, input):
    encoder = IncrementalEncoder(errors="raises")
    with pytest.raises(EncodingError):
        encoder.encode(input, final=True)
    assert 0 == encoder.getstate()


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [(u"+", b"?", 1), (u"a+b", b"1?23", 3), (u"a+n", b"15?", 3)],
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
        ((b"", 0), b"", u""),
        ((b"", 0x1000035), b"a", u"15"),
        ((b"", 0x1000035), b"na", u"155"),
        ((b"", 0x1000036000037), b"na", u"1567"),
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
    [(b"", u"", 0), (b"a", u"1", 1), (b"b", u"23", 1), (b"ab", u"123", 2)],
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
    [(b"+", u"\uFFFD", 1), (b"a+b", u"1\uFFFD23", 3), (b"an+", u"1\uFFFD5", 3)],
)
def test_decode_invalid_with_replacement(input, expected, expected_len):
    decoder = IncrementalDecoder(errors="replace")
    output = decoder.decode(input)
    assert expected == output
    assert (b"", 0) == decoder.getstate()
