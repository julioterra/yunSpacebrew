r"""UUID objects (universally unique identifiers) according to RFC 4122.

This module provides immutable UUID objects (class UUID) and the functions
uuid4(), uuid5() for generating version 4 UUIDs as specified in RFC 4122.
The method uuid4() creates a random UUID.

based on work from 'Ka-Ping Yee <ping@zesty.ca>'

"""
class UUID4(object):
    """Instances of the UUID class represent UUIDs as specified in RFC 4122.
    UUID objects are immutable, hashable, and usable as dictionary keys.
    Converting a UUID to a string with str() yields something in the form
    '12345678-1234-1234-1234-123456789abc'.  The UUID constructor accepts
    five possible forms: a similar string of hexadecimal digits, or a tuple
    of six integer fields (with 32-bit, 16-bit, 16-bit, 8-bit, 8-bit, and
    48-bit values respectively) as an argument named 'fields', or a string
    of 16 bytes (with all the integer fields in big-endian order) as an
    argument named 'bytes', or a string of 16 bytes (with the first three
    fields in little-endian order) as an argument named 'bytes_le', or a
    single 128-bit integer as an argument named 'int'.

    UUIDs have these read-only attributes:

        bytes       the UUID as a 16-byte string (containing the six
                    integer fields in big-endian byte order)
    """

    def __init__(self, bytes=None):
        version = 4

        if bytes is not None:
            if len(bytes) != 16:
                raise ValueError('bytes is not a 16-char string')
            int = long(('%02x'*16) % tuple(map(ord, bytes)), 16)

        if version is not None:
            if not 1 <= version <= 5:
                raise ValueError('illegal version number')

            # Set the variant to RFC 4122.
            int &= ~(0xc000 << 48L)
            int |= 0x8000 << 48L

            # Set the version number.
            int &= ~(0xf000 << 64L)
            int |= version << 76L

        self.__dict__['int'] = int

    def __cmp__(self, other):
        if isinstance(other, UUID):
            return cmp(self.int, other.int)
        return NotImplemented

    def __hash__(self):
        return hash(self.int)

    def __int__(self):
        return self.int

    def __str__(self):
        hex = '%032x' % self.int
        return '%s-%s-%s-%s-%s' % (
            hex[:8], hex[8:12], hex[12:16], hex[16:20], hex[20:])

    def get_bytes(self):
        bytes = ''
        for shift in range(0, 128, 8):
            bytes = chr((self.int >> shift) & 0xff) + bytes
        return bytes

    bytes = property(get_bytes)


def uuid4():
    """Generate a random UUID."""

    # Otherwise, get randomness from urandom or the 'random' module.
    try:
        import os
        return UUID4(bytes=os.urandom(16))
    except:
        import random
        bytes = [chr(random.randrange(256)) for i in range(16)]
        return UUID4(bytes=bytes)