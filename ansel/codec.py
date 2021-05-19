import codecs

from .incremental import IncrementalDecoder, IncrementalEncoder


class Codec(codecs.Codec):
    name = None
    encode_char_map = {}
    encode_modifier_map = {}
    decode_char_map = {}
    decode_control_map = {}
    decode_modifier_map = {}

    def encode(self, input, errors="strict"):
        encoder = IncrementalEncoder(errors)
        encoder.name = self.name
        encoder.encode_char_map = self.encode_char_map
        encoder.encode_modifier_map = self.encode_modifier_map
        return encoder.encode(input, final=True), len(input)

    def decode(self, input, errors="strict"):
        decoder = IncrementalDecoder(errors)
        decoder.name = self.name
        decoder.decode_char_map = self.decode_char_map
        decoder.decode_control_map = self.decode_control_map
        decoder.decode_modifier_map = self.decode_modifier_map
        return decoder.decode(input, final=True), len(input)
