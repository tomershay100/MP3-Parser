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
        self.__pcm_data: np.array = np.array([])
        self.__file_length: int = 0
        self.__file_path = file_path
        self.__new_file_path = self.__file_path[:-4] + '.wav'

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
                # print(f'Parsed: {num_of_parsed_frames}')

            pcm_data.extend(list(self.__curr_frame.pcm.copy()))

        self.__pcm_data = np.array(pcm_data)

        return num_of_parsed_frames

    def write_to_wav(self):
        # Convert PCM to WAV
        write(self.__new_file_path, self.__curr_frame.sampling_rate, self.__pcm_data.astype(np.float32))
