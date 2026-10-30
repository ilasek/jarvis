"""Turn text into a raw audio clip for the board using the macOS `say` voice.

Usage: python3 tools/make_voice.py "Hello, I'm Jarvis" firmware/hello.pcm [--voice Daniel]

Output is 16 kHz, mono, signed 16-bit little-endian PCM with no header,
the format firmware/sound.py plays.
"""
import argparse
import array
import pathlib
import subprocess
import tempfile
import wave

RATE = 16000
# Full-scale speech is loud enough on this amp to risk browning out USB power.
GAIN = 0.4


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('text')
    parser.add_argument('output')
    parser.add_argument('--voice', default='Daniel')
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        aiff = pathlib.Path(tmp) / 'speech.aiff'
        wav = pathlib.Path(tmp) / 'speech.wav'
        subprocess.run(['say', '-v', args.voice, '-o', str(aiff), args.text], check=True)
        subprocess.run(['afconvert', '-f', 'WAVE', '-d', f'LEI16@{RATE}', '-c', '1',
                        str(aiff), str(wav)], check=True)
        with wave.open(str(wav)) as w:
            samples = array.array('h', w.readframes(w.getnframes()))

    for i, s in enumerate(samples):
        samples[i] = int(s * GAIN)
    pathlib.Path(args.output).write_bytes(samples.tobytes())
    print(f'wrote {args.output}: {len(samples) / RATE:.1f} s, {len(samples) * 2} bytes')


if __name__ == '__main__':
    main()
