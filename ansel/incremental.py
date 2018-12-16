import codecs


class IncrementalDecoder(codecs.IncrementalDecoder):
    name = None
    decode_char_map = {}
    decode_modifier_map = {}

    def __init__(self, errors="strict"):
        super().__init__(errors)
        self.decoded_modifiers = []

    def getstate(self):
        if not self.decoded_modifiers:
            return (b"", 0)
        state = 1
        for item in self.decoded_modifiers:
            for char in item:
                state <<= 24
                state += ord(char)
        return (b"", state)

    def setstate(self, state):
        decoded_modifiers = []
        _, state = state
        while state > 1:
            char = state & 0xFFFFFF
            state >>= 24
            decoded_modifiers.append(chr(char))
        decoded_modifiers.reverse()
        self.decoded_modifiers = decoded_modifiers

    def decode(self, input, final=False):
        error_handler = codecs.lookup_error(self.errors)
        decoded_chars = []
        for index, item in enumerate(input):
            try:
                decoded_item = self.decode_char_map[bytes([item])]
                decoded_chars.append(decoded_item)
                decoded_chars += self.decoded_modifiers
                self.decoded_modifiers.clear()
            except KeyError:
                try:
                    decoded_item = self.decode_modifier_map[bytes([item])]
                    self.decoded_modifiers.insert(0, decoded_item)
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
                    decoded_chars += self.decoded_modifiers
                    self.decoded_modifiers.clear()

        if final:
            decoded_chars += self.decoded_modifiers
            self.decoded_modifiers.clear()

        return "".join(decoded_chars)


class IncrementalEncoder(codecs.IncrementalEncoder):
    name = None
    encode_char_map = {}
    encode_modifier_map = {}

    def __init__(self, errors="strict"):
        super().__init__(errors)
        self.current_char = []

    def getstate(self):
        if not self.current_char:
            return 0
        state = 1
        for item in self.current_char:
            for byte in item:
                state <<= 8
                state += byte
        return state

    def setstate(self, state):
        current_char = []
        while state > 1:
            byte = state & 0xFF
            state >>= 8
            current_char.append(bytes([byte]))
        current_char.reverse()
        self.current_char = current_char

    def encode(self, input, final=False):
        error_handler = codecs.lookup_error(self.errors)
        encoded_chars = []
        current_char = []
        for index, item in enumerate(input):
            try:
                encoded_item = self.encode_char_map[item]
                encoded_chars += self.current_char
                self.current_char = [encoded_item]
            except KeyError:
                try:
                    self.current_char.insert(0, self.encode_modifier_map[item])
                except KeyError:
                    try:
                        item, _ = error_handler(
                            UnicodeEncodeError(
                                self.name,
                                input,
                                index,
                                index + 1,
                                "character maps to <undefined>",
                            )
                        )
                        encoded_item = self.encode(item)
                        encoded_chars.append(encoded_item)
                    except UnicodeEncodeError:
                        self.current_char = []
                        raise

        if final:
            encoded_chars += self.current_char
            self.current_char = []

        return b"".join(encoded_chars)
