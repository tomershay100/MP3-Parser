import sys


class Offset:
    def __init__(self):
        self.__offset: int = 0

    @property
    def offset(self):
        return self.__offset

    def add_to_offset(self, n):
        self.__offset += n


def bytes_to_int(byte_list: bytes):
    return int.from_bytes(byte_list, sys.byteorder)


def get_bits(buffer: list, start_bit: int, end_bit: int):
    start_byte = start_bit >> 3
    end_byte = end_bit >> 3
    start_bit = start_bit % 8
    end_bit = end_bit % 8

    # Get the bits slice
    result = (bytes_to_int(buffer[start_byte]) << (32 - (8 - start_bit))) >> (32 - (8 - start_bit))

    if start_byte != end_byte:
        while start_byte != end_byte:
            result <<= 8
            result += bytes_to_int(buffer[start_byte])
            start_byte += 1
        result <<= end_bit
        result += bytes_to_int(buffer[end_byte]) >> (8 - end_bit)
    elif end_bit != 8:
        result >>= (8 - end_bit)

    return result




