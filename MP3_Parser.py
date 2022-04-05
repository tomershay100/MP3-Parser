from tables import *

from enum import Enum
import math

import numpy as np

NUM_PREV_FRAMES = 9
NUM_OF_FREQUENCIES = 576


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


class Band:
    def __init__(self):
        self.long_win: list = []
        self.short_win: list = []


class FrameHeader:
    def __init__(self):
        # Declarations
        self.__buffer: list = []
        self.__mpeg_version: float = 0.0
        self.__layer: int = 0
        self.__crc: bool = False
        self.__bit_rate: int = 0
        self.__sampling_rate: int = 0
        self.__padding: bool = False
        self.__channel_mode: ChannelMode = ChannelMode(0)
        self.__channels: int = 0
        self.__mode_extension: list = [0, 0]
        self.__emphasis: Emphasis = Emphasis(0)
        self.__info: list = [False, False, False]
        self.__band_index: Band = Band()
        self.__band_width: Band = Band()

    # Unpack the MP3 header.
    # @param buffer A pointer that points to the first byte of the frame header.
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

    # Cyclic redundancy check. If set, two bytes after the header information are used up by the CRC.
    def __set_crc(self):
        self.__crc = self.__buffer[1] & 0x01

    # Additional information (not important)
    def __set_info(self):
        self.__info = [self.__buffer[2] & 0x01, self.__buffer[3] & 0x08, self.__buffer[3] & 0x04]

    # Although rarely used, there is no method for emphasis.
    def __set_emphasis(self):
        value = (self.__buffer[3] << 6) >> 6
        self.__emphasis = Emphasis(value)

    def __set_sampling_rate(self):
        rates = [[44100, 48000, 32000], [22050, 24000, 16000], [11025, 12000, 8000]]
        ceil_mpeg_version = int(math.floor(self.__mpeg_version))
        if (self.__buffer[2] & 0x08) != 0x08 and (self.__buffer[2] & 0x04) != 0x04:
            self.__sampling_rate = rates[ceil_mpeg_version - 1][0]
        elif (self.__buffer[2] & 0x08) != 0x08 and (self.__buffer[2] & 0x04) == 0x04:
            self.__sampling_rate = rates[ceil_mpeg_version - 1][1]
        elif (self.__buffer[2] & 0x08) == 0x08 and (self.__buffer[2] & 0x04) != 0x04:
            self.__sampling_rate = rates[ceil_mpeg_version - 1][2]

    # During the decoding process different tables are used depending on the sampling rate.
    def __set_tables(self):
        if self.__sampling_rate == 32000:
            self.__band_index.short_win = band_index_table.short_32
            self.__band_width.short_win = band_width_table.short_32
            self.__band_index.long_win = band_index_table.long_32
            self.__band_width.long_win = band_width_table.long_32
        elif self.__sampling_rate == 44100:
            self.__band_index.short_win = band_index_table.short_44
            self.__band_width.short_win = band_width_table.short_44
            self.__band_index.long_win = band_index_table.long_44
            self.__band_width.long_win = band_width_table.long_44
        elif self.__sampling_rate == 48000:
            self.__band_index.short_win = band_index_table.short_48
            self.__band_width.short_win = band_width_table.short_48
            self.__band_index.long_win = band_index_table.long_48
            self.__band_width.long_win = band_width_table.long_48

    # 0 -> Stereo
    # 1 -> Joint stereo (this option requires use of mode_extension)
    # 2 -> Dual channel
    # 3 -> Single channel
    def __set_channel_mode(self):
        value = self.__buffer[3] >> 6
        self.__channel_mode = ChannelMode(value)
        self.__channels = 1 if self.__channel_mode == ChannelMode.Mono else 2

    # Applies only to joint stereo.
    def __set_mode_extension(self):
        if self.__layer == 3:
            self.__mode_extension = [self.__buffer[3] & 0x20, self.__buffer[3] & 0x10]

    # If set, the frame size is 1 byte larger.
    def __set_padding(self):
        self.__padding = self.__buffer[2] & 0x02

    # For variable bit rate (VBR) files, this data has to be gathered constantly.
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

    @property
    def layer(self):
        return self.__layer

    @property
    def bit_rate(self):
        return self.__bit_rate

    @property
    def sampling_rate(self):
        return self.__sampling_rate

    @property
    def mpeg_version(self):
        return self.__mpeg_version

    @property
    def padding(self):
        return self.__padding


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
    def main_data_begin(self):
        return self.__main_data_begin

    @main_data_begin.setter
    def main_data_begin(self, main_data_begin):
        self.__main_data_begin = main_data_begin


class MP3Parser:

    def __init__(self, buffer):
        # Declarations
        self.__curr_header: FrameHeader = FrameHeader()
        self.__curr_frame: Frame = Frame()
        self.__valid: bool = False
        self.__buffer: list

        if buffer[0] == 0xFF and buffer[1] >= 0xE0:
            self.__valid = True
            self.__curr_frame.frame_size = 0
            self.__curr_frame.main_data_begin = 0
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

    @property
    def get_buffer(self):
        return self.__buffer

    def set_buffer(self, buffer):
        self.__buffer = buffer


buffer = [0] * 1000
buffer[0], buffer[1] = 0xFF, 0xE0
decoder = MP3Parser(buffer)
pass

print('[2][2] int', np.array([[0] * 2] * 2).shape)
print('[2][2] bool', np.array([[False] * 2] * 2).shape)
print('[2][4] bool', np.array([[False] * 4] * 2).shape)
print('[2][2][3] int', np.array([[3 * [0]] * 2] * 2).shape)
print('[2][2][22] int', np.array([[22 * [0]] * 2] * 2).shape)
print('[2][2][3][13] int', np.array([[[13 * [0]] * 3] * 2] * 2).shape)
