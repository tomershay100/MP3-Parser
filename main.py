from MP3_Parser import MP3Parser

buffer = [0xFF, 0xE0]
for i in range(1000):
    buffer.append(0x00)

buffer = bytes(buffer)

decoder = MP3Parser(buffer)
pass
decoder.init_frame()
pass
