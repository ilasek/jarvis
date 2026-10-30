"""Copy every file in firmware/ onto the board's MicroPython filesystem, then hard-reset it.

Usage: python3 tools/deploy.py [--port /dev/cu.usbmodemXXXX]
"""
import argparse
import binascii
import glob
import pathlib
import sys
import time

import serial

FIRMWARE_DIR = pathlib.Path(__file__).resolve().parent.parent / 'firmware'
CHUNK = 2048


class RawRepl:
    def __init__(self, port):
        self.serial = serial.Serial(port, 115200, timeout=0.2)
        self.serial.write(b'\r\x03\x03')
        time.sleep(0.3)
        self.serial.reset_input_buffer()
        self.serial.write(b'\x01')
        self._read_until(b'raw REPL; CTRL-B to exit\r\n>')

    def _read_until(self, marker, timeout=10):
        data = b''
        end = time.time() + timeout
        while not data.endswith(marker):
            if time.time() > end:
                raise TimeoutError(f'no response from board (got {data[-200:]!r})')
            data += self.serial.read(1)
        return data

    def exec(self, code):
        self.serial.write(code.encode() + b'\x04')
        self._read_until(b'OK')
        out = self._read_until(b'\x04')[:-1]
        err = self._read_until(b'\x04>')[:-2]
        if err:
            raise RuntimeError(err.decode(errors='replace'))
        return out.decode(errors='replace')

    def reset(self):
        self.serial.write(b'import machine; machine.reset()\x04')
        time.sleep(0.5)
        self.serial.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port')
    args = parser.parse_args()
    port = args.port or next(iter(sorted(glob.glob('/dev/cu.usbmodem*'))), None)
    if not port:
        sys.exit('No board found. Is it plugged in?')

    files = sorted(p for p in FIRMWARE_DIR.iterdir() if p.is_file() and not p.name.startswith('.'))
    repl = RawRepl(port)
    repl.exec('import ubinascii')
    for path in files:
        data = path.read_bytes()
        repl.exec(f"f = open('{path.name}', 'wb')")
        for i in range(0, len(data), CHUNK):
            b64 = binascii.b2a_base64(data[i:i + CHUNK], newline=False).decode()
            repl.exec(f"f.write(ubinascii.a2b_base64('{b64}'))")
        repl.exec('f.close()')
        print(f'uploaded {path.name} ({len(data)} bytes)')
    repl.reset()
    print(f'board on {port} restarted')


if __name__ == '__main__':
    main()
