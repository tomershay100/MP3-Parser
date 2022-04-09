import util
from FrameHeader import *
from FrameSideInformation import FrameSideInformation
import numpy as np

NUM_PREV_FRAMES = 9
NUM_OF_FREQUENCIES = 576


class Frame:
    def __init__(self):
        # Declarations
        self.__buffer: list = []
        self.__prev_frame_size: np.ndarray = np.zeros(NUM_PREV_FRAMES)
        self.__frame_size: int = 0
        self.__side_info: FrameSideInformation = FrameSideInformation()
        self.__prev_samples: np.ndarray = np.zeros((2, 32, 18))
        self.__fifo: np.ndarray = np.zeros((2, 1024))

        self.__main_data: list = []
        self.__samples: np.ndarray = np.zeros((2, 2, NUM_OF_FREQUENCIES))
        self.__pcm: np.ndarray = np.zeros((NUM_OF_FREQUENCIES * 4))

    def init_frame_params(self, buffer, header):
        self.__buffer = buffer
        self.__set_frame_size(header)

        starting_side_info_idx = 6 if header.crc == 0 else 4
        self.__side_info.set_side_info(self.__buffer[starting_side_info_idx:], header)
        self.__set_main_data(header, [0])

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

        self.frame_size = int(((samples_per_frame / 8) * header.bit_rate) / header.sampling_rate)
        if header.padding == 1:
            self.frame_size += 1

    # Due to the Huffman bits' varying length the main_data isn't aligned with the frames.
    # Unpacks the scaling factors and quantized samples.
    def __set_main_data(self, header: FrameHeader, last_buffer: list):
        constant = 21 if header.channel_mode == ChannelMode.Mono else 36
        if header.crc == 0:
            constant += 2

        # We'll put the main data in its own buffer. Main data may be larger than the previous frame and doesn't
        # Include the size of side info and headers
        if self.__side_info.main_data_begin == 0:
            self.__main_data = self.__buffer[constant: self.frame_size - constant]
        # TODO this requires getting last frame buffer from parser class
        # else:
        #     bound = 0
        #     for frame in range(NUM_PREV_FRAMES):
        #         bound += self.prev_frame_size[frame] - constant
        #         if self.__side_info.main_data_begin < bound:
        #             ptr_offset = self.__side_info.main_data_begin + frame * constant
        #             buffer_offset = 0
        #
        #             # TODO change to numpy array
        #             part = [[0] * NUM_PREV_FRAMES]
        #             part[frame] = self.__side_info.main_data_begin
        #             for i in range(frame):
        #                 part[i] = self.prev_frame_size[i] - constant
        #                 part[frame] -= part[i]
        #
        #             self.__main_data = last_buffer[len(last_buffer) - ptr_offset: part[frame]]
        #             ptr_offset -= (part[frame] + constant)
        #             for i in range(frame-1, -1, -1):
        #                 self.__main_data.extend(last_buffer[len(last_buffer) - ptr_offset: part[i]])
        #                 ptr_offset -= (part[i] + constant)
        #             self.__main_data.extend((self.__buffer[constant: self.frame_size - constant]))
        #             break

        # bit = 0
        # for gr in range(2):
        #     for ch in range(header.channels):
        #         max_bit = bit + side_info.part2_3_length[gr][ch]
        #         bit = unpack_scalefac(gr, ch, bit)
        #         unpack_samples(header, gr, ch, bit, max_bit)
        #         bit = max_bit

    # Unpack the scale factor indices from the main data. slen1 and slen2 are the size (in bits) of each scaling factor.
    # There are 21 scaling factors for long windows and 12 for each short window.
    def __unpack_scalefac(self, gr: int, ch: int, bit: int):
        sfb = 0
        window = 0
        scalefactor_length = [slen[self.__side_info.scalefac_compress[gr][ch]][0],
                              slen[self.__side_info.scalefac_compress[gr][ch]][1]]

        # No scale factor transmission for short blocks.
        if self.__side_info.block_type[gr][ch] == 2 and self.__side_info.window_switching[gr][ch]:
            if self.__side_info.mixed_block_flag[gr][ch] == 1:  # Mixed blocks.
                for sfb in range(8):
                    self.__side_info.scalefac_l[gr][ch][sfb] = util.get_bits(self.__main_data, bit,
                                                                             scalefactor_length[0])
                    bit += scalefactor_length[0]

                for sfb in range(3, 6):
                    for window in range(3):
                        self.__side_info.scalefac_s[gr][ch][window][sfb] = util.get_bits(self.__main_data, bit,
                                                                                         scalefactor_length[0])
                        bit += scalefactor_length[0]
            else:  # Short blocks.
                for sfb in range(6):
                    for window in range(3):
                        self.__side_info.scalefac_s[gr][ch][window][sfb] = util.get_bits(self.__main_data, bit,
                                                                                         scalefactor_length[0])
                        bit += scalefactor_length[0]

            for sfb in range(6, 12):
                for window in range(3):
                    self.__side_info.scalefac_s[gr][ch][window][sfb] = util.get_bits(self.__main_data, bit,
                                                                                     scalefactor_length[1])
                    bit += scalefactor_length[1]

            for window in range(3):
                self.__side_info.scalefac_s[gr][ch][window][12] = 0

        # Scale factors for long blocks.
        else:
            if gr == 0:
                for sfb in range(11):
                    self.__side_info.scalefac_l[gr][ch][sfb] = util.get_bits(self.__main_data, bit,
                                                                             scalefactor_length[0])
                    bit += scalefactor_length[0]
                for sfb in range(11, 21):
                    self.__side_info.scalefac_l[gr][ch][sfb] = util.get_bits(self.__main_data, bit,
                                                                             scalefactor_length[1])
                    bit += scalefactor_length[1]
            else:  # Scale factors might be reused in the second granule.
                SB = [6, 11, 16, 21]
                for i in range(2):
                    for sfb in range(SB[i]):
                        if self.__side_info.scfsi[ch][i]:
                            self.__side_info.scalefac_l[gr][ch][sfb] = self.__side_info.scalefac_l[0][ch][sfb]
                        else:
                            self.__side_info.scalefac_l[gr][ch][sfb] = util.get_bits(self.__main_data, bit,
                                                                                     scalefactor_length[0])
                            bit += scalefactor_length[0]
                for i in range(2, 4):
                    for sfb in range(SB[1], SB[i]):
                        if self.__side_info.scfsi[ch][i]:
                            self.__side_info.scalefac_l[gr][ch][sfb] = self.__side_info.scalefac_l[0][ch][sfb]
                        else:
                            self.__side_info.scalefac_l[gr][ch][sfb] = util.get_bits(self.__main_data, bit,
                                                                                     scalefactor_length[1])
                            bit += scalefactor_length[1]

            self.__side_info.scalefac_l[gr][ch][21] = 0

    def __unpack_samples(self, header: FrameHeader, gr, ch, bit, max_bit):
        # Get big value region boundaries.
        if self.side_info.window_switching[gr][ch] and self.side_info.block_type[gr][ch] == 2:
            region0 = 36
            region1 = 576
        else:
            region0 = header.band_index.long_win[self.side_info.region0_count[gr][ch] + 1]
            region1 = header.band_index.long_win[self.side_info.region0_count[gr][ch] + 1 +
                                                 self.side_info.region1_count[gr[ch] + 1]]
        # TODO continue from here

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
