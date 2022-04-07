import sys


BYTE_LENGTH = 8


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


def right_shift_char(a: bytes, b: int):
    result_int = int.from_bytes(a, byteorder="big") >> b
    return result_int.to_bytes(len(a), byteorder="big")


def left_shift_char(a: bytes, b: int):
    result_int = int.from_bytes(a, byteorder="big") << b
    return result_int.to_bytes(len(a), byteorder="big")


def get_bits(buffer: list, start_bit: int, slice_len: int):
    # exclude the last bit of the slice
    end_bit = start_bit + slice_len - 1
    start_byte = start_bit >> 3
    end_byte = end_bit >> 3
    bits = []
    for idx in range(start_byte, end_byte + 1):
        num = buffer[idx]
        curr_bits = 8
        out = [1 if num & (1 << (curr_bits - 1 - n)) else 0 for n in range(curr_bits)]
        bits.extend(out)
    result = 0
    slice = bits[start_bit:end_bit + 1]
    slice.reverse()

    for i in range(len(slice)):
        result += (2 ** i) * slice[i]

    return result
