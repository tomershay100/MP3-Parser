# import numpy as np
from Frame import *
from scipy.io.wavfile import write

HEADER_SIZE = 4


class MP3Parser:

    def __init__(self, file_data, offset, file_path):
        # Declarations
        # self.__curr_header: FrameHeader = FrameHeader()
        self.__curr_frame: Frame = Frame()
        self.__valid: bool = False
        # List of integers that contain the file (without ID3) data
        self.__file_data: list = []
        self.__buffer: list = []
        self.__file_length: int = 0
        self.file_path = file_path

        # cut the id3 from hex_data
        self.__buffer = file_data[offset:]

        if self.__buffer[0] == 0xFF and self.__buffer[1] >= 0xE0:
            self.__valid = True
            self.__file_data = file_data
            self.__file_length = len(file_data)
            self.__offset = offset
            self.__init_curr_header()
            self.__curr_frame.set_frame_size()
        else:
            self.__valid = False

    def __init_curr_header(self):
        if self.__buffer[0] == 0xFF and self.__buffer[1] >= 0xE0:
            self.__curr_frame.init_header_params(self.__buffer)
        else:
            self.__valid = False

    def __init_curr_frame(self):
        self.__curr_frame.init_frame_params(self.__buffer, self.__file_data, self.__offset)

    # TODO return pcm
    def parse_file(self):
        pcm_data = []
        num_of_parsed_frames = 0

        while self.__valid and self.__file_length > self.__offset + HEADER_SIZE:
            self.__init_curr_header()
            if self.__valid:
                self.__init_curr_frame()
                num_of_parsed_frames += 1
                self.__offset += self.__curr_frame.frame_size
                self.__buffer = self.__file_data[self.__offset:]

            pcm_data.extend(list(self.__curr_frame.pcm.copy()))

        pcm_data = np.array(pcm_data)
        new_file_path = self.file_path[:-4] + '.wav'
        write(new_file_path, self.__curr_frame.sampling_rate, pcm_data.astype(np.float32))
        return num_of_parsed_frames

# buffer = [0] * 1000
# buffer[0], buffer[1] = 0xFF, 0xE0
# self = MP3Parser(buffer)
# pass
#
# print('[2][2] int', np.array([[0] * 2] * 2).shape)
# print('[2][2] bool', np.array([[False] * 2] * 2).shape)
# print('[2][4] bool', np.array([[False] * 4] * 2).shape)
# print('[2][2][3] int', np.array([[3 * [0]] * 2] * 2).shape)
# print('[2][2][22] int', np.array([[22 * [0]] * 2] * 2).shape)
# print('[2][2][3][13] int', np.array([[[13 * [0]] * 3] * 2] * 2).shape)
