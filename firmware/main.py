import time
from machine import Pin, I2C

import face
from display import SH1107
from sound import Speaker

DISPLAY_SDA = 5   # XIAO D4
DISPLAY_SCL = 6   # XIAO D5
SPEAKER_BCLK = 7  # XIAO D8
SPEAKER_LRC = 4   # XIAO D3
SPEAKER_DIN = 2   # XIAO D1
BOOT_BUTTON = 0   # XIAO BOOT button

GREETING = 'hello.pcm'
GREETING_PAUSE_MS = 5000


def main():
    if Pin(BOOT_BUTTON, Pin.IN, Pin.PULL_UP).value() == 0:
        print('Safe mode: BOOT button held at startup, firmware not started.')
        return
    oled = SH1107(I2C(0, sda=Pin(DISPLAY_SDA), scl=Pin(DISPLAY_SCL), freq=400000))
    face.draw(oled)
    oled.wake()
    oled.setup()
    oled.show()
    speaker = Speaker(SPEAKER_BCLK, SPEAKER_LRC, SPEAKER_DIN)
    while True:
        # While lit, the display disturbs the amp through the shared 5V/GND
        # wiring and the speech is garbled or silent (also with the amp on 3V3),
        # so it is switched off for the duration of each clip. Playback in turn
        # corrupts the display's memory, so the face is redrawn afterwards.
        oled.wake()
        oled.power_off()
        speaker.play(GREETING)
        oled.wake()
        oled.setup()
        oled.show()
        oled.power_on()
        time.sleep_ms(GREETING_PAUSE_MS)


main()
