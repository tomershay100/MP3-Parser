from enum import Enum
from tables import *

# import numpy as np

MAX_VERSION = 3


class ChannelMode(Enum):
    Stereo = 0
    JointStereo = 1
    DualChannel = 2
    Mono = 3


class Emphasis(Enum):
    NONE = 0
    MS5015 = 1
    Reserved = 2
    CCITJ17 = 3


class Band_Index:
    def __init__(self):
        self.long_win: int
        self.short_win: int


class FrameHeader:
    def __init__(self):
        # Declarations
        self.__buffer: list
        self.__mpeg_version: float
        self.__layer: int
        self.__crc: bool
        self.__sampling_rate: int
        self.__padding: bool
        self.__channel_mode: ChannelMode
        self.__channels: int
        self.__mode_extension: list
        self.__emphasis: Emphasis
        self.__info: list

    def init_header_params(self, buffer):
        self.__buffer = buffer
        self.__set_mpeg_version()
        self.__set_layer(self.__buffer[1])
        self.__set_crc()
        self.__set_info()
        self.__set_emphasis()
        self.__set_sampling_rate()
        self.__set_tables()
        self.__set_channel_mode()
        self.__set_mode_extension()
        self.__set_padding()
        self.__set_bit_rate()
        self.__set_frame_size()

    # Determine the MPEG version.
    def __set_mpeg_version(self):
        if (self.__buffer[1] & 0x10) == 0x10 and (self.__buffer[1] & 0x08) == 0x08:
            self.__mpeg_version = 1
        elif (self.__buffer[1] & 0x10) == 0x10 and (self.__buffer[1] & 0x08) != 0x08:
            self.__mpeg_version = 2
        elif (self.__buffer[1] & 0x10) != 0x10 and (self.__buffer[1] & 0x08) == 0x08:
            self.__mpeg_version = 0
        elif (self.__buffer[1] & 0x10) != 0x10 and (self.__buffer[1] & 0x08) != 0x08:
            self.__mpeg_version = 2.5

    # Determine layer
    def __set_layer(self, byte):
        byte = byte << 5
        byte = byte >> 6
        self.__layer = 4 - byte

    def __set_crc(self):
        self.__crc = self.__buffer[1] & 0x01

    def __set_info(self):
        self.__info = [self.__buffer[2] & 0x01, self.__buffer[3] & 0x08, self.__buffer[3] & 0x04]

    def __set_emphasis(self):
        value = (self.__buffer[3] << 6) >> 6
        self.__emphasis = Emphasis(value)

    def __set_sampling_rate(self):
        rates = [[44100, 48000, 32000], [22050, 24000, 16000], [11025, 12000, 8000]]
        if (self.__buffer[2] & 0x08) != 0x08 and (self.__buffer[2] & 0x04) != 0x04:
            self.__sampling_rate = rates[self.__mpeg_version - 1][0]
        elif (self.__buffer[2] & 0x08) != 0x08 and (self.__buffer[2] & 0x04) == 0x04:
            self.__sampling_rate = rates[self.__mpeg_version - 1][1]
        elif (self.__buffer[2] & 0x08) == 0x08 and (self.__buffer[2] & 0x04) != 0x04:
            self.__sampling_rate = rates[self.__mpeg_version - 1][2]

    # During the decoding process different tables are used depending on the sampling rate.
    def __set_tables(self):
        pass

    def __set_channel_mode(self):
        value = self.__buffer[3] >> 6
        self.__channel_mode = ChannelMode(value)
        self.__channels = 1 if self.__channel_mode == ChannelMode.Mono else 2

    def __set_mode_extension(self):
        if self.__layer == 3:
            self.__mode_extension = [self.__buffer[3] & 0x20, self.__buffer[3] & 0x10]

    def __set_padding(self):
        self.__padding = self.__buffer[2] & 0x02

    def __set_bit_rate(self):
        if self.__mpeg_version == 1:
            if self.__layer == 1:
                self.__bit_rate = self.__buffer[2] * 32
            elif self.__layer == 2:
                rates = [32, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 384]
                self.__bit_rate = rates[(self.__buffer[2] >> 4) - 1] * 1000
            elif self.__layer == 3:
                rates = [32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320]
                self.__bit_rate = rates[(self.__buffer[2] >> 4) - 1] * 1000
            else:
                self.__valid = False
        else:
            if self.__layer == 1:
                rates = [32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320]
                self.__bit_rate = rates[(self.__buffer[2] >> 4) - 1] * 1000
            elif self.__layer < 4:
                rates = [8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160]
                self.__bit_rate = rates[(self.__buffer[2] >> 4) - 1] * 1000
            else:
                self.__valid = False


class FrameSideInfo:
    def __init__(self):
        # Declarations
        self.__buffer: list
        self.__prev_frame_size: list
        self.__frame_size: int
        self.__main_data_begin: int
        self.__scfsi: list

        # Allocate space for two granules and two channels.
        self.__part2_3_length: list
        self.__part2_length: list
        self.__big_value: list
        self.__global_gain: list
        self.__scalefac_compress: list
        self.__slen1: list
        self.__slen2: list
        self.__window_switching: list
        self.__block_type: list
        self.__mixed_block_flag: list
        self.__switch_point_l: list
        self.__switch_point_s: list
        self.__table_select: list
        self.__region0_count: list
        self.__region1_count: list
        self.__preflag: list
        self.__scalefac_scale: list
        self.__count1table_select: list

        self.__scalefac_l: list
        self.__scalefac_s: list

    @property
    def frame_size(self):
        return self.__frame_size

    @frame_size.setter
    def frame_size(self, frame_size):
        self.__frame_size = frame_size

    @property
    def main_data_begin(self):
        return self.__main_data_begin

    @main_data_begin.setter
    def main_data_begin(self, main_data_begin):
        self.__main_data_begin = main_data_begin


class MP3Parser:

    def __init__(self, buffer):
        # Declarations
        self.__curr_header: FrameHeader
        self.__curr_frame: FrameSideInfo
        self.__buffer: list
        self.__valid: bool
        self.__buffer: list

        # Frame
        self.__prev_samples: list
        self.__fifo: list

        self.__main_data: list
        self.__samples: list
        self.__pcm: list

        self.__curr_header = FrameHeader()
        self.__curr_side_info = FrameSideInfo()

        if buffer[0] == 0xFF and buffer[1] >= 0xE0:
            self.__valid = True
            self.__curr_side_info.frame_size = 0
            self.__curr_side_info.main_data_begin = 0
            self.__buffer = buffer
            self.__curr_header.init_header_params(self.__buffer)
        else:
            self.__valid = False

    @property
    def get_buffer(self):
        return self.__buffer

    def set_buffer(self, buffer):
        self.__buffer = buffer


