# import numpy as np
from Frame import *
from FrameHeader import *


class MP3Parser:

    def __init__(self, buffer):
        # Declarations
        self.__curr_header: FrameHeader = FrameHeader()
        self.__curr_frame: Frame = Frame()
        self.__valid: bool = False
        self.__buffer: list

        if buffer[0] == 0xFF and buffer[1] >= 0xE0:
            self.__valid = True
            self.__buffer = buffer
            self.__curr_header.init_header_params(self.__buffer)
            self.__set_frame_size()

        else:
            self.__valid = False

    def initialize(self, buffer):
        self.__buffer = buffer
        self.__curr_header.init_header_params(self.__buffer)
        self.__set_frame_size()

    # Determine the frame size.
    def __set_frame_size(self):
        samples_per_frame = 0

        if self.__curr_header.layer == 3:
            if self.__curr_header.mpeg_version == 1:
                samples_per_frame = 1152
            else:
                samples_per_frame = 576

        elif self.__curr_header.layer == 2:
            samples_per_frame = 1152

        elif self.__curr_header.layer == 1:
            samples_per_frame = 384

        # Minimum frame size = 1152 / 8 * 32000 / 48000 = 96
        # Minimum main_data size = 96 - 36 - 2 = 58
        # Maximum main_data_begin = 2^9 = 512
        # Therefore remember ceil(512 / 58) = 9 previous frames.
        for i in range(NUM_PREV_FRAMES - 1, 0, -1):
            self.__curr_frame.prev_frame_size[i] = self.__curr_frame.prev_frame_size[i - 1]
        self.__curr_frame.prev_frame_size[0] = self.__curr_frame.frame_size

        self.__curr_frame.frame_size = ((
                                                samples_per_frame / 8) * self.__curr_header.bit_rate) / self.__curr_header.sampling_rate
        if self.__curr_header.padding == 1:
            self.__curr_frame.frame_size += 1

    def unpack_scalefac(self, gr: int, ch: int):
        # No scale factor transmissions for short blocks
        pass

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
