from FrameSideInformation import FrameSideInformation

NUM_PREV_FRAMES = 9
NUM_OF_FREQUENCIES = 576


class Frame:
    def __init__(self):
        # Declarations
        self.__buffer: list = []
        self.__prev_frame_size: list = [0] * NUM_PREV_FRAMES
        self.__frame_size: int = 0
        self.__side_info: FrameSideInformation = FrameSideInformation()

        self.__prev_samples: list = [[18 * [0.0]] * 32] * 2
        self.__fifo: list = [[0.0] * 1024] * 2

        self.__main_data: bytes = bytes()
        self.__samples: list = [[NUM_OF_FREQUENCIES * [0.0]] * 2] * 2
        self.__pcm: list = [NUM_OF_FREQUENCIES * 4 * [0.0]]

    def init_frame_params(self, buffer, header):
        self.__buffer = buffer
        self.__set_frame_size(header)

        starting_side_info_idx = 6 if header.crc == 0 else 4
        self.__side_info.set_side_info(self.__buffer[starting_side_info_idx:], header)

    # Determine the frame size.
    def __set_frame_size(self, header):
        samples_per_frame = 0

        if header.layer == 3:
            if header.mpeg_version == 1:
                samples_per_frame = 1152
            else:
                samples_per_frame = 576

        elif header.layer == 2:
            samples_per_frame = 1152

        elif header.layer == 1:
            samples_per_frame = 384

        # Minimum frame size = 1152 / 8 * 32000 / 48000 = 96
        # Minimum main_data size = 96 - 36 - 2 = 58
        # Maximum main_data_begin = 2^9 = 512
        # Therefore remember ceil(512 / 58) = 9 previous frames.
        for i in range(NUM_PREV_FRAMES - 1, 0, -1):
            self.prev_frame_size[i] = self.prev_frame_size[i - 1]
        self.prev_frame_size[0] = self.frame_size

        self.frame_size = ((samples_per_frame / 8) * header.bit_rate) / header.sampling_rate
        if header.padding == 1:
            self.frame_size += 1

    @property
    def frame_size(self):
        return self.__frame_size

    @frame_size.setter
    def frame_size(self, frame_size):
        self.__frame_size = frame_size

    @property
    def prev_frame_size(self):
        return self.__prev_frame_size

    @prev_frame_size.setter
    def prev_frame_size(self, prev_frame_size):
        self.__prev_frame_size = prev_frame_size

    @property
    def side_info(self):
        return self.__side_info
