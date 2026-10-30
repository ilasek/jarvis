import framebuf

WIDTH = 128
HEIGHT = 128
ADDRESS = 0x3C

SETUP_COMMANDS = (
    (0x20,),        # page addressing mode
    (0x81, 0x80),   # contrast
    (0xA0,),        # segment remap normal
    (0xC0,),        # COM scan direction normal
    (0xA8, 0x7F),   # multiplex ratio: 128 rows
    (0xD3, 0x00),   # display offset
    (0xDC, 0x00),   # display start line
    (0xA4,),        # show RAM contents
    (0xA6,),        # not inverted
)


class SH1107(framebuf.FrameBuffer):
    def __init__(self, i2c, address=ADDRESS, retries=5):
        self.i2c = i2c
        self.address = address
        self.retries = retries
        self.buffer = bytearray(WIDTH * HEIGHT // 8)
        self._pages = memoryview(self.buffer)
        super().__init__(self.buffer, WIDTH, HEIGHT, framebuf.MONO_VLSB)

    # This display's I2C link drops individual transfers, so every write is retried.
    def _write(self, *parts):
        for _ in range(self.retries):
            try:
                self.i2c.writevto(self.address, parts)
                return True
            except OSError:
                pass
        return False

    # The first transfers after the bus has been idle are often lost; a burst of
    # address-only probes beforehand makes the following writes reliable.
    def wake(self):
        self.i2c.scan()
        self.i2c.scan()

    def command(self, *bytes_):
        return self._write(b'\x00', bytes(bytes_))

    def setup(self):
        for cmd in SETUP_COMMANDS:
            self.command(*cmd)

    def show(self):
        for page in range(HEIGHT // 8):
            self.command(0xB0 | page, 0x00, 0x10)
            self._write(b'\x40', self._pages[page * WIDTH:(page + 1) * WIDTH])

    def power_on(self):
        return self.command(0xAF)

    def power_off(self):
        return self.command(0xAE)
