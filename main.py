import sys
import time

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


    decoder = MP3Parser(hex_data, offset)

    start = time.time()
    num_of_parsed_frames = decoder.parse_file(offset)
    parsing_time = time.time() - start
    print('Parsed', num_of_parsed_frames, 'frames in', parsing_time, 'seconds')
