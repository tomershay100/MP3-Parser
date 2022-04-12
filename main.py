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

    ################################

    # id3_decoder = ID3(hex_data)
    # offset = id3_decoder.get_offset()

    offset = 148
    decoder = MP3Parser(hex_data, offset,file_path)

    start = time.time()
    num_of_parsed_frames = decoder.parse_file()
    parsing_time = time.time() - start
    print('Parsed', num_of_parsed_frames, 'frames in', parsing_time, 'seconds')
