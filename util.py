import sys
import math


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
    for i in range(0, slice_len):
        result += 2 ** i * bits[i]

    return result

    # # Get the bits slice
    # result = (((buffer[start_byte] << (32 - (8 - start_bit))) % 32) >> (32 - (8 - start_bit))) % 32
    #
    # if start_byte != end_byte:
    #     start_byte += 1
    #     while start_byte != end_byte:
    #         result <<= 8
    #         result += buffer[start_byte]
    #         start_byte += 1
    #     result <<= end_bit
    #     result += buffer[end_byte] >> (8 - end_bit)
    # elif end_bit != 8:
    #     result >>= (8 - end_bit)
    #
    # return result
