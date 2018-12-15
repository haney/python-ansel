import codecs


class Codec(codecs.Codec):
    name = None
    encode_char_map = {}
    encode_modifier_map = {}
    decode_char_map = {}
    decode_modifier_map = {}

    def encode(self, input, errors="strict"):
        error_handler = codecs.lookup_error(errors)
        encoded_chars = []
        encoded_modifiers = []
        delayed_chars = []
        for index, item in enumerate(input):
            try:
                encoded_item = self.encode_char_map[item]
                encoded_chars += encoded_modifiers
                encoded_modifiers.clear()
                encoded_chars += delayed_chars
                delayed_chars.clear()
                delayed_chars.append(encoded_item)
            except KeyError:
                try:
                    encoded_modifiers.insert(0, self.encode_modifier_map[item])
                except KeyError:
                    item, _ = error_handler(
                        UnicodeEncodeError(
                            self.name,
                            input,
                            index,
                            index + 1,
                            "character maps to <undefined>",
                        )
                    )
                    encoded_item, _ = self.encode(item)
                    encoded_chars += encoded_modifiers
                    encoded_modifiers.clear()
                    encoded_chars += delayed_chars
                    delayed_chars.clear()
                    delayed_chars.append(encoded_item)

        encoded_chars += encoded_modifiers
        encoded_chars += delayed_chars

        return b"".join(encoded_chars), len(input)

    def decode(self, input, errors="strict"):
        error_handler = codecs.lookup_error(errors)
        decoded_chars = []
        decoded_modifiers = []
        for index, item in enumerate(input):
            try:
                decoded_item = self.decode_char_map[bytes([item])]
                decoded_chars.append(decoded_item)
                decoded_chars += decoded_modifiers
                decoded_modifiers.clear()
            except KeyError:
                try:
                    decoded_item = self.decode_modifier_map[bytes([item])]
                    decoded_modifiers.insert(0, decoded_item)
                except KeyError:
                    decoded_item, _ = error_handler(
                        UnicodeDecodeError(
                            self.name,
                            input,
                            index,
                            index + 1,
                            "character maps to <undefined>",
                        )
                    )
                    decoded_chars.append(decoded_item)
                    decoded_chars += decoded_modifiers
                    decoded_modifiers.clear()

        decoded_chars += decoded_modifiers
        return "".join(decoded_chars), len(input)
