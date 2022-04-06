# from MP3_Parser import MP3Parser
#
# buffer = [0xFF, 0xE0]
# for i in range(1000):
#     buffer.append(0x00)
#
# buffer = bytes(buffer)
#
# decoder = MP3Parser(buffer)
# pass
# decoder.init_frame()
# pass


import sys

from MP3_Parser import MP3Parser
from ID3_Parser import ID3

if __name__ == '__main__':
    if len(sys.argv) > 2:
        print("Unexpected number of arguments.")
        exit(-1)
    if len(sys.argv) < 2:
        print("No directory specified.")
        exit(-1)
    file_path = sys.argv[1]

    with open(file_path, 'rb') as f:
        hex_data = [c for c in f.read()]

    # id3_decoder = ID3(hex_data)
    # offset = id3_decoder.get_offset()
    offset = 148

    buffer = hex_data[offset:]  # cut the id3 from hex_data
    decoder = MP3Parser(buffer)
    decoder.init_header(buffer)
    decoder.init_frame()

    offset+=decoder.get_frame_size()
    decoder.init_header(buffer)
    decoder.init_frame()

    buffer = [0] * 1000
    buffer[0], buffer[1] = 0xFF, 0xE0
    decoder1 = MP3Parser(buffer)
