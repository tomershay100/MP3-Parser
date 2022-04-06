# import numpy as np
from Frame import *
from FrameHeader import *


class MP3Parser:

    def __init__(self, buffer):
        # Declarations
        self.__curr_header: FrameHeader = FrameHeader()
        self.__curr_frame: Frame = Frame()
        self.__valid: bool = False
        self.__buffer: list = []

        if buffer[0] == 0xFF and buffer[1] >= 0xE0:
            self.__valid = True
            self.__buffer = buffer
            self.__curr_header.init_header_params(self.__buffer)

        else:
            self.__valid = False

    def init_header(self, buffer):
        if buffer[0] == 0xFF and buffer[1] >= 0xE0:
            self.__buffer = buffer
            self.__curr_header.init_header_params(self.__buffer)
        else:
            self.__valid = False

    def init_frame(self):
        self.__curr_frame.init_frame_params(self.__buffer, self.__curr_header)

    def unpack_scalefac(self, gr: int, ch: int):
        # No scale factor transmissions for short blocks
        pass
    def get_frame_size(self):
        return self.__curr_frame.frame_size
# buffer = [0] * 1000
# buffer[0], buffer[1] = 0xFF, 0xE0
# decoder = MP3Parser(buffer)
# pass
#
# print('[2][2] int', np.array([[0] * 2] * 2).shape)
# print('[2][2] bool', np.array([[False] * 2] * 2).shape)
# print('[2][4] bool', np.array([[False] * 4] * 2).shape)
# print('[2][2][3] int', np.array([[3 * [0]] * 2] * 2).shape)
# print('[2][2][22] int', np.array([[22 * [0]] * 2] * 2).shape)
# print('[2][2][3][13] int', np.array([[[13 * [0]] * 3] * 2] * 2).shape)
