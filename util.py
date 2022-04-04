import sys


def bytes_to_int(byte_list: bytes):
    return int.from_bytes(byte_list, sys.byteorder)
