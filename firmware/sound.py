from machine import I2S, Pin

RATE = 16000
BUFFER_BYTES = 16000
CHUNK_BYTES = 4096


class Speaker:
    def __init__(self, bclk, lrc, din):
        self.pins = (bclk, lrc, din)
        self.chunk = memoryview(bytearray(CHUNK_BYTES))
        self._quiet()

    def _quiet(self):
        # Floating amp inputs make the speaker hum; hold them low while idle.
        for pin in self.pins:
            Pin(pin, Pin.OUT, value=0)

    def play(self, path):
        """Play a raw 16 kHz mono 16-bit clip (see tools/make_voice.py). Blocks until done."""
        bclk, lrc, din = self.pins
        audio = I2S(0, sck=Pin(bclk), ws=Pin(lrc), sd=Pin(din), mode=I2S.TX,
                    bits=16, format=I2S.MONO, rate=RATE, ibuf=BUFFER_BYTES)
        try:
            with open(path, 'rb') as f:
                while True:
                    n = f.readinto(self.chunk)
                    if not n:
                        break
                    audio.write(self.chunk[:n])
            # write() returns once data is queued; a buffer of silence makes
            # sure the end of the clip has played before the I2S is stopped.
            audio.write(bytes(BUFFER_BYTES))
        finally:
            audio.deinit()
            self._quiet()
