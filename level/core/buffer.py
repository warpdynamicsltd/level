class BufferException(Exception):
    pass


class Buffer:
    def __init__(self, offset):
        self.offset = offset
        self.cursor = self.offset
        self.buffer = {}
        self.max_index = -1

    def set_cursor(self, cursor):
        if cursor < self.offset:
            raise BufferException("Cursor can't be less then offset")

        self.cursor = cursor

    def move_cursor(self, shift):
        self.cursor += shift

        if self.cursor < self.offset:
            raise BufferException("Cursor can't be less then offset")

    def put_byte(self, b):
        self.buffer[self.cursor] = b
        if self.cursor > self.max_index:
            self.max_index = self.cursor
        self.cursor += 1

    def write(self, bs):
        for b in bs:
            self.put_byte(b)

    def get_bytes(self):
        begin = self.offset
        end = self.max_index
        result = bytearray(end - begin + 1)
        for i in range(len(result)):
            k = i + self.offset
            if k in self.buffer:
                result[i] = self.buffer[k]

        return result
