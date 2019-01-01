import codecs

from . import ansel
from .. import codec, incremental

GEDCOM_TO_UNICODE = ansel.ANSEL_TO_UNICODE.copy()
GEDCOM_TO_UNICODE.update(
    {
        b"\xBE": u"\u25A1",  # WHITE SQUARE
        b"\xBF": u"\u25A0",  # BLACK SQUARE
        b"\xCD": u"\u0065",  # LATIN SMALL LETTER E
        b"\xCE": u"\u006F",  # LATIN SMALL LETTER O
        b"\xCF": u"\u00DF",  # LATIN SMALL LETTER SHARP S
    }
)

GEDCOM_TO_UNICODE_MODIFIERS = ansel.ANSEL_TO_UNICODE_MODIFIERS.copy()
GEDCOM_TO_UNICODE_MODIFIERS.update(
    {b"\xFC": u"\u0338"}  # COMBINING LONG SOLIDUS OVERLAY
)

UNICODE_TO_GEDCOM = ansel.UNICODE_TO_ANSEL.copy()
UNICODE_TO_GEDCOM.update(
    {
        u"\u00DF": b"\xCF",  # LATIN SMALL LETTER SHARP S
        u"\u2260": b"\xFC\x3D",  # NOT EQUAL TO
        u"\u226E": b"\xFC\x3C",  # NOT LESS-THAN
        u"\u226F": b"\xFC\x3E",  # NOT GREATER-THAN
        u"\u25A0": b"\xBF",  # BLACK SQUARE
        u"\u25A1": b"\xBE",  # WHITE SQUARE
    }
)

UNICODE_TO_GEDCOM_MODIFIERS = ansel.UNICODE_TO_ANSEL_MODIFIERS.copy()
UNICODE_TO_GEDCOM_MODIFIERS.update(
    {u"\u0338": b"\xFC"}  # COMBINING LONG SOLIDUS OVERLAY
)


class Codec(codec.Codec):
    name = "gedcom"
    encode_char_map = UNICODE_TO_GEDCOM
    encode_modifier_map = UNICODE_TO_GEDCOM_MODIFIERS
    decode_char_map = GEDCOM_TO_UNICODE
    decode_modifier_map = GEDCOM_TO_UNICODE_MODIFIERS


class IncrementalDecoder(incremental.IncrementalDecoder):
    name = "gedcom"
    decode_char_map = GEDCOM_TO_UNICODE
    decode_modifier_map = GEDCOM_TO_UNICODE_MODIFIERS


class IncrementalEncoder(incremental.IncrementalEncoder):
    name = "gedcom"
    encode_char_map = UNICODE_TO_GEDCOM
    encode_modifier_map = UNICODE_TO_GEDCOM_MODIFIERS


class StreamReader(Codec, codecs.StreamReader):
    pass


class StreamWriter(Codec, codecs.StreamWriter):
    pass


def getregentry():
    return codecs.CodecInfo(
        name="gedcom",
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
