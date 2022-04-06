class FrameSideInformation:
    def __init__(self):
        self.__main_data_begin: int = 0
        self.__scfsi: list = [[False] * 4] * 2

        # Side Info for the two granules. Allocate space for two granules and two channels.
        self.__part2_3_length: list = [[0] * 2] * 2
        self.__part2_length: list = [[0] * 2] * 2
        self.__big_value: list = [[0] * 2] * 2
        self.__global_gain: list = [[0] * 2] * 2
        self.__scalefac_compress: list = [[0] * 2] * 2
        self.__slen1: list = [[0] * 2] * 2
        self.__slen2: list = [[0] * 2] * 2
        self.__window_switching: list = [[False] * 2] * 2
        self.__block_type: list = [[0] * 2] * 2
        self.__mixed_block_flag: list = [[False] * 2] * 2
        self.__switch_point_l: list = [[0] * 2] * 2
        self.__switch_point_s: list = [[0] * 2] * 2
        self.__table_select: list = [[3 * [0]] * 2] * 2
        self.__subblock_gain: list = [[3 * [0]] * 2] * 2
        self.__region0_count: list = [[0] * 2] * 2
        self.__region1_count: list = [[0] * 2] * 2
        self.__preflag: list = [[0] * 2] * 2
        self.__scalefac_scale: list = [[0] * 2] * 2
        self.__count1table_select: list = [[0] * 2] * 2

        self.__scalefac_l: list = [[22 * [0]] * 2] * 2
        self.__scalefac_s: list = [[[13 * [0]] * 3] * 2] * 2

    @property
    def main_data_begin(self):
        return self.__main_data_begin

    @main_data_begin.setter
    def main_data_begin(self, main_data_begin):
        self.__main_data_begin = main_data_begin
