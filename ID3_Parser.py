import sys
# from enum import Enum
from util import bytes_to_int

MPEG_VERSION = 2


# class ID3Flags(Enum):
#     FooterPresent = 0
#     ExperimentalIndicator = 1
#     ExtendedHeader = 2
#     Unsynchronisation = 3


class ID3Frame:
    def __init__(self, frame_id: str, flags: bytes, content: bytes):
        self.__frame_id: str = frame_id
        self.__frame_flags: tuple = self.__set_flags(flags)
        self.__content: bytes = content

    def __set_flags(self, flags: bytes):
        flags = bytes_to_int(flags)
        frame_flags = []
        for bit_num in range(3):
            if flags >> bit_num & 1:
                frame_flags.append(True)
            else:
                frame_flags.append(False)
        for bit_num in range(8, 11):
            if flags >> bit_num & 1:
                frame_flags.append(True)
            else:
                frame_flags.append(False)

        return tuple(frame_flags)

    @property
    def __get_id(self):
        return self.__frame_id

    @property
    def __get_content(self):
        return self.__content


class ID3:
    # TODO add getters
    # TODO parse extended header
    def __init__(self, buffer: list):
        # Declarations
        self.__buffer: list = buffer
        self.__offset: int
        self.__valid: bool
        self.__start: int
        self.__version: str
        self.__id3_flags: list = []
        self.__extended_header_size: int
        self.__id3_frames: list = []

        if str(buffer[0]) == 'I' and str(buffer[1]) == 'D' and str(buffer[2]) == '3':
            self.__set_version(self.__buffer[3], self.__buffer[4])
            if self.__set_flags(self.__buffer[5]):
                self.__valid = True
                self.__set_offset(self.__buffer[6])
                self.__set_extended_header_size(self.__buffer[7])
                self.__set_frames(10 + self.__extended_header_size)
            else:
                self.__valid = False
        else:
            self.__valid = False

    def __set_version(self, version: bytes, revision: bytes):
        self.__version = f'{MPEG_VERSION}%{version.decode()}%{revision.decode()}'

    def __set_offset(self, offset: bytes):
        self.__offset = bytes_to_int(offset)

    def __set_flags(self, flags: bytes):
        flags = bytes_to_int(flags)

        # These flags must be unset for frame to be valid (protected bits)
        for bit_num in range(4):
            if flags >> bit_num & 1:
                return False
        # Check flags
        for bit_num in range(4, 8):
            self.__id3_flags[bit_num - 4] = flags >> bit_num & 1

        self.__id3_flags = tuple(self.__id3_flags)
        return True

    def __set_extended_header_size(self, size: bytes):
        size = bytes_to_int(size)

        # TODO change to Enum
        if self.__id3_flags[2]:
            self.__extended_header_size = size
        else:
            self.__extended_header_size = 0

    def __set_frames(self, start):
        # TODO change to Enum
        footer_size = self.__id3_flags[0] * 10
        size = self.__offset - self.__extended_header_size - footer_size
        i = 0

        while i < size:
            frame_id = str(self.__buffer[start + i: start + i + 4])
            for c in frame_id:
                if not (c.isupper() or c.isdigit()):  # Check for legal ID
                    break
            i += 4
            field_size = bytes_to_int(self.__buffer[start + i: start + i + 4])
            i += 4
            frame_flags = self.__buffer[start + i: start + i + 2]
            i += 2
            frame_content = self.__buffer[start + i: start + i + field_size]
            i += field_size
            self.__id3_frames.append(ID3Frame(frame_id, frame_flags, frame_content))











