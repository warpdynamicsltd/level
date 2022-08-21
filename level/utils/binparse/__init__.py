from types import SimpleNamespace
import struct


class BinParseException(Exception):
    pass


class BinParse:
    BIG_ENDIAN = 1
    LITTLE_ENDIAN = -1

    ACTIVE = 1
    PASSIVE = 0

    def __init__(self, block, offset=0, endianness=LITTLE_ENDIAN, mode=PASSIVE, meta=None):
        self.level = 0
        self.leaf = True
        self.size = 0
        self.meta = meta
        self.mode = mode
        self.block = block
        self.offset = int(offset)
        self.cursor = 0
        self.endianness = endianness
        self.build()
        self.size = self.cursor

    def build(self):
        pass

    def align(self, base):
        r = self.cursor % base
        self.cursor += (base - r)

    def prepare_get(self):
        self.cursor = 0
        self.build()

    def set(self, obj):
        if issubclass(type(obj), BinParse) and self.size == obj.size:
            self.cursor = 0
            self.block[self.offset:self.offset + obj.size] = obj.block[obj.offset:obj.offset + obj.size]
            #self.size = obj.size
            return

        attrb = f"set_from_{type(obj).__name__}"
        if hasattr(type(self), attrb):
            set_method = getattr(type(self), attrb)
            set_method(self, obj)
            return

        if hasattr(type(self), 'default_set'):
            self.default_set(obj)
            return

        raise BinParseException("Can't find set instructions")

    def struct_get(self, fmt, size):
        if self.endianness == BinParse.LITTLE_ENDIAN:
            fmt = '<' + fmt
        else:
            fmt = '>' + fmt

        return struct.unpack(fmt, self.block[self.offset:self.offset + size])[0]

    def struct_set(self, fmt, size, value):
        if self.endianness == BinParse.LITTLE_ENDIAN:
            fmt = '<' + fmt
        else:
            fmt = '>' + fmt

        buffer = struct.pack(fmt, value)
        self.block[self.offset:self.offset + size] = buffer

    def reg(self, name, cls, offset, endianness='inherit'):
        if endianness == 'inherit':
            endianness = self.endianness

        obj = cls(block=self.block,
                  offset=offset,
                  endianness=endianness,
                  mode=self.mode,
                  meta=self.meta)

        self._reg(name, obj)
        return obj.size

    def add(self, name, cls, endianness='inherit'):
        size = self.reg(name, cls, self.offset + self.cursor, endianness)
        if size == 0:
            print(cls)
        self.update_cursor(size)

    def reg_array(self, name, cls, length, offset, endianness='inherit'):
        if endianness == 'inherit':
            endianness = self.endianness

        array = Array(self.block,
                      cls,
                      length=length,
                      offset=offset,
                      endianness=endianness,
                      mode=self.mode,
                      meta=self.meta)

        self._reg(name, array)
        return array.size

    def add_array(self, name, cls, length, endianness='inherit'):
        size = self.reg_array(name, cls, length, self.offset + self.cursor, endianness)
        self.update_cursor(size)

    def add_byte_data_fast(self, name, payload):
        size = len(payload)
        self.block[self.cursor:self.cursor + size] = payload
        setattr(self, name, SimpleNamespace(offset=self.cursor, size=size))
        self.update_cursor(size)

    def update_cursor(self, size):
        if self.size > 0:
            size = self.size
        if size > 0:
            self.cursor += size
        else:
            raise BinParseException("Unknown Length")

    def _reg(self, name, obj):
        setattr(self, f'_binparse_{name}', obj)

        self.leaf = False

        def _set(s, _obj):
            x = getattr(s, f'_binparse_{name}')
            x.set(_obj)

        def _get(s):
            return getattr(s, f'_binparse_{name}')

        def _del(s):
            delattr(s, f'_binparse_{name}')

        setattr(self.__class__, name, property(_get, _set, _del))

    def __len__(self):
        return self.size

    def __bytes__(self):
        return bytes(self.block[self.offset:self.offset + self.size])

    def repr(self, level):
        res = ""
        for name in dir(self):
            if '_binparse_' in name:
                r = getattr(self, name).repr(level + 1)
                if r == "":
                    res += " " * level + f"{type(self).__name__}.{name[10:]} = {repr(getattr(self, name))}\n"
                else:
                    res += " " * level + f"{type(self).__name__}.{name[10:]} = \n"
                    res += r

        return res

    def __repr__(self):
        # res = ""
        # for name in dir(self):
        #     if '_binparse_' in name:
        #         res += f"{type(self).__name__}.{name[10:]} = {repr(getattr(self, name))}\n"
        res = ""
        for name in dir(self):
            if '_binparse_' in name:
                obj = getattr(self, name)
                obj.level = self.level + 1
                if obj.leaf:
                    res += "  " * self.level + f"|-{type(self).__name__}.{name[10:]} = {repr(obj)}\n"
                else:
                    res += "  " * self.level + f"|-{type(self).__name__}.{name[10:]} = \n"
                    res += repr(obj)

        return res


class Array(BinParse):
    def __init__(self,
                 block,
                 cls,
                 length,
                 offset=0,
                 endianness=BinParse.LITTLE_ENDIAN,
                 mode='passive',
                 meta=None):
        self.length = int(length)
        self.cls = cls
        BinParse.__init__(self, block, offset, endianness, mode, meta)
        if self.cls is BYTE:
            self.leaf = True

    def build(self):
        for i in range(self.length):
            self.add(f'0x{i:08x}', self.cls)

    def __getitem__(self, i):
        i = int(i)
        if i < 0 or i >= len(self):
            raise IndexError()
        return getattr(self, f'0x{i:08x}')

    def __setitem__(self, i, value):
        i = int(i)
        if type(value) is BinParse:
        # setattr(self, f'element_{i}', value)
            self._reg(f'0x{i:08x}', value)
        else:
            setattr(self, f'0x{i:08x}', value)

    def __len__(self):
        return self.length

    def __repr__(self):
        if self.cls is BYTE:
            return repr(list(self))
        else:
            return BinParse.__repr__(self)

    def set(self, seq):
        for i, x in enumerate(seq):
            self[i] = x


class _IntType(BinParse):
    def __repr__(self):
        return str(int(self))

    def __index__(self):
        return int(self)

    def __eq__(self, other):
        return int(self) == int(other)

    def __add__(self, other):
        return int(self) + int(other)

    def __sub__(self, other):
        return int(self) - int(other)


class SZ(BinParse):
    def build(self):
        self.cursor = 0
        if self.mode == BinParse.ACTIVE:
            self.cursor = 0
        else:
            while self.block[self.offset + self.cursor] != 0:
                self.cursor += 1

    def __str__(self):
        return str(self.block[self.offset:self.offset + self.size], encoding='ASCII')

    def __repr__(self):
        return f"'{str(self)}'"

    def default_set(self, value):
        value = str(value)
        self.cursor = 0
        self.block[self.offset: self.offset + len(value)] = bytes(value, encoding='ASCII')
        self.block[self.offset + len(value)] = 0
        self.size = len(value) + 1


class BYTE(BinParse):
    def build(self):
        self.cursor = 1

    def __repr__(self):
        b = self.struct_get('B', self.size)
        return "0x%02x" % b

    def default_set(self, value):
        self.struct_set('B', self.size, int(value))


class CHAR(BinParse):
    def build(self):
        self.cursor = 1

    def __str__(self):
        return str(self.struct_get('c', self.size), encoding='ASCII')

    def __repr__(self):
        return f"'{str(self)}'"

    def default_set(self, value):
        self.struct_set('c', self.size, bytes(value, encoding='ASCII'))


class UINT8(_IntType):
    def build(self):
        self.cursor = 1

    def __int__(self):
        return self.struct_get('B', self.size)

    def default_set(self, value):
        self.struct_set('B', self.size, int(value))

    def pupa(self):
        pass


class INT8(_IntType):
    def build(self):
        self.cursor = 1

    def __int__(self):
        return self.struct_get('b', self.size)

    def default_set(self, value):
        self.struct_set('b', self.size, int(value))


class UINT16(_IntType):
    def build(self):
        self.cursor = 2

    def __int__(self):
        return self.struct_get('H', self.size)

    def default_set(self, value):
        self.struct_set('H', self.size, int(value))


class INT16(_IntType):
    def build(self):
        self.cursor = 2

    def __int__(self):
        return self.struct_get('h', self.size)

    def default_set(self, value):
        self.struct_set('h', self.size, int(value))


class UINT32(_IntType):
    def build(self):
        self.cursor = 4

    def __int__(self):
        return self.struct_get('I', self.size)

    def default_set(self, value):
        self.struct_set('I', self.size, int(value))


class INT32(_IntType):
    def build(self):
        self.cursor = 4

    def __int__(self):
        return self.struct_get('i', self.size)

    def default_set(self, value):
        self.struct_set('i', self.size, int(value))


class UINT64(_IntType):
    def build(self):
        self.cursor = 8

    def __int__(self):
        return self.struct_get('Q', self.size)

    def default_set(self, value):
        self.struct_set('Q', self.size, int(value))


class INT64(_IntType):
    def build(self):
        self.cursor = 8

    def __int__(self):
        return self.struct_get('q', self.size)

    def default_set(self, value):
        self.struct_set('q', self.size, int(value))

