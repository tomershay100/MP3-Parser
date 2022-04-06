from FrameSideInformation import FrameSideInformation

NUM_PREV_FRAMES = 9
NUM_OF_FREQUENCIES = 576


class Frame:
    def __init__(self):
        # Declarations
        self.__buffer: list
        self.__prev_frame_size: list = [0] * NUM_PREV_FRAMES
        self.__frame_size: int = 0
        self.__side_info: FrameSideInformation = FrameSideInformation()

        self.__prev_samples: list = [[18 * [0.0]] * 32] * 2
        self.__fifo: list = [[0.0] * 1024] * 2

        self.__main_data: list = []
        self.__samples: list = [[NUM_OF_FREQUENCIES * [0.0]] * 2] * 2
        self.__pcm: list = [NUM_OF_FREQUENCIES * 4 * [0.0]]

    def init_frame_params(self, buffer, header):
        self.__buffer = buffer

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
