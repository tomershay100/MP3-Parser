from enum import Enum


class ChannelMode(Enum):
    Stereo = 0
    JointStereo = 1
    DualChannel = 2
    Mono = 3


class Emphasis(Enum):
    none = 0
    MS5015 = 1
    Reserved = 2
    CCITJ17 = 3


class Band_Index():
    def __init__(self):
        self.long_win: int
        self.short_win: int


class MP3_Parser:

    def __init__(self, buffer):
        # fields
        self.__buffer: list
        self.__valid: bool
        self.__mpeg_version: float
        self.__layer: int
        self.__crc: bool
        self.__sampling_rate: int
        self.__padding: bool
        self.__channel_mode: ChannelMode
        self.__channels: int
        self.__mode_extension: list
        self.__emphasis: Emphasis


