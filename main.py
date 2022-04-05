from MP3_Parser import MP3Parser

buffer = [0] * 1000
buffer[0], buffer[1] = 0xFF, 0xE0
decoder = MP3Parser(buffer)
pass

