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

    # buffer = hex_data[offset:]  # cut the id3 from hex_data
    # decoder = MP3Parser(buffer)
    # decoder.init_header(buffer)
    # decoder.init_frame()
    #
    # offset += decoder.get_frame_size()
    # buffer = hex_data[offset:]
    # decoder.init_header(buffer)
    # decoder.init_frame()
    # pass

    ################################

    file_length = len(hex_data)
    buffer = hex_data[offset:]  # cut the id3 from hex_data
    decoder = MP3Parser(buffer)
    i = 0
    while decoder.is_valid() and file_length > offset + decoder.get_header_size():
        decoder.init_header(buffer)
        if decoder.is_valid():
            decoder.init_frame()
            i += 1
            print('Parsed', i, 'th frame', 'offset', offset)
            offset += decoder.get_frame_size()
            buffer = hex_data[offset:]

pass

