from ansel.codec import Codec
import pytest
import codecs


class TestCodec(Codec):
    name = "test"
    encode_char_map = {"a": b"1", "b": b"23", "?": b"?"}
    decode_char_map = {b"a": "1", b"b": "23"}
    encode_modifier_map = {"n": b"5", "o": b"67"}
    decode_modifier_map = {b"n": "5", b"o": "67"}


class EncodingError(BaseException):
    pass


def error_handler_raises(exception):
    raise EncodingError()


codecs.register_error("raises", error_handler_raises)


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [("", b"", 0), ("a", b"1", 1), ("b", b"23", 1), ("ab", b"123", 2)],
)
def test_encode_valid(input, expected, expected_len):
    codec = TestCodec()
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
    codec = TestCodec()
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
    codec = TestCodec()
    with pytest.raises(UnicodeEncodeError) as exc_info:
        codec.encode(input)
    assert "test" == exc_info.value.encoding
    assert reason == exc_info.value.reason
    assert input == exc_info.value.object
    assert start == exc_info.value.start
    assert end == exc_info.value.end


@pytest.mark.parametrize("input", ["+"])
def test_encode_invalid_raising_error_handler(input):
    codec = TestCodec()
    with pytest.raises(EncodingError):
        codec.encode(input, errors="raises")


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [("+", b"?", 1), ("a+b", b"1?23", 3), ("a+n", b"15?", 3)],
)
def test_encode_invalid_with_replacement(input, expected, expected_len):
    codec = TestCodec()
    output, output_len = codec.encode(input, errors="replace")
    assert expected == output
    assert expected_len == output_len


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [(b"", "", 0), (b"a", "1", 1), (b"b", "23", 1), (b"ab", "123", 2)],
)
def test_decode_valid(input, expected, expected_len):
    codec = TestCodec()
    output, output_len = codec.decode(input)
    assert expected == output
    assert expected_len == output_len


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [
        (b"n", "5", 1),
        (b"an", "15", 2),
        (b"bn", "235", 2),
        (b"na", "15", 2),
        (b"naa", "151", 3),
        (b"noa", "1675", 3),
        (b"onb", "23567", 3),
    ],
)
def test_decode_valid_with_modifiers(input, expected, expected_len):
    codec = TestCodec()
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
    codec = TestCodec()
    with pytest.raises(UnicodeDecodeError) as exc_info:
        codec.decode(input)
    assert "test" == exc_info.value.encoding
    assert reason == exc_info.value.reason
    assert input == exc_info.value.object
    assert start == exc_info.value.start
    assert end == exc_info.value.end


@pytest.mark.parametrize("input", [b"+"])
def test_decode_invalid_raising_error_handler(input):
    codec = TestCodec()
    with pytest.raises(EncodingError):
        codec.decode(input, errors="raises")


@pytest.mark.parametrize(
    "input, expected, expected_len",
    [(b"+", "\uFFFD", 1), (b"a+b", "1\uFFFD23", 3), (b"an+", "1\uFFFD5", 3)],
)
def test_decode_invalid_with_replacement(input, expected, expected_len):
    codec = TestCodec()
    output, output_len = codec.decode(input, errors="replace")
    assert expected == output
    assert expected_len == output_len
