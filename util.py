import numpy as np
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


# def get_bits(buffer: list, start_bit: int, slice_len: int):
#     end_bit = start_bit + slice_len - 1
#     start_byte = start_bit >> 3
#     end_byte = end_bit >> 3
#     start_bit = start_bit % 8
#     end_bit = end_bit % 8
#
#     # Get the bits slice
#     result = (buffer[start_byte] << (32 - (8 - start_bit))) >> (32 - (8 - start_bit))
#
#     if start_byte != end_byte:
#         start_byte += 1
#         while start_byte != end_byte:
#             result <<= 8
#             result += buffer[start_byte]
#             start_byte += 1
#         result <<= end_bit
#         result += buffer[end_byte] >> (8 - end_bit)
#     elif end_bit != 8:
#         result >>= (8 - end_bit)
#
#     return result

def get_bits(buffer: list, start_bit: int, slice_len: int):
    # exclude the last bit of the slice
    end_bit = start_bit + slice_len - 1
    if type(start_bit) != int:
        pass
    start_byte = start_bit >> 3
    end_byte = end_bit >> 3

    bits = []
    for idx in range(start_byte, end_byte + 1):
        num = buffer[idx]
        out = [1 if num & (1 << (BYTE_LENGTH - 1 - n)) else 0 for n in range(BYTE_LENGTH)]
        bits.extend(out)

    # update to relative positions in the bits array
    start_bit %= 8
    end_bit = start_bit + slice_len - 1

    bit_slice = bits[start_bit:end_bit + 1]

    result = 0

    bit_slice.reverse()

    for i in range(len(bit_slice)):
        result += (2 ** i) * bit_slice[i]

    return result
