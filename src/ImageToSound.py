import math
import struct
import wave
import itertools
import sys
import multiprocessing

from functools import reduce
from PIL import Image
from tqdm import tqdm


class ImageToSound:
    def __init__(self, args):
        self.args = args
        self.total_pixels = 0
        self.total_frames = self.args.framerate * self.args.duration

    def run(self):
        channels = self.freq_from_file(self.args.infile)
        samples = self.compute_channel(channels)

        self.write_wavefile(self.args.outfile, samples, self.args.framerate * self.args.duration,
                            framerate=self.args.framerate)

    def freq_from_file(self, file):
        img = Image.open(file)
        cur_freq = 0
        self.total_pixels = reduce(lambda x, y: x*y, img.size)

        for pixel in tqdm((x for x in img.getdata()), total=self.total_pixels, desc="Converting Image",
                          dynamic_ncols=True, leave=True):
            cur_freq = 0
            for band in pixel:
                cur_freq += band
            yield self.sine_wave_gen(cur_freq, self.args.framerate, self.args.duration)

    @staticmethod
    def sine_wave_gen(frequency, framerate=44100, duration=1, amplitude=1):
        for i in range(framerate * duration):
            yield math.sin(2.0 * math.pi * float(frequency) * (float(i) / float(framerate))) * float(amplitude)

    def compute_channel(self, channels):
        for gen in tqdm(((x for x in y) for y in zip(*channels)), total=self.total_frames, desc="Combining Waves",
                        dynamic_ncols=True, leave=True):
            yield sum(gen) / self.total_frames

    @staticmethod
    def grouper(group_size, iterable, fill_val=None):
        args = [iter(iterable)] * group_size
        return itertools.zip_longest(*args, fillvalue=fill_val)

    def write_wavefile(self, filename, samples, nframes=None, nchannels=2, sampwidth=2, framerate=44100, bufsize=2048):
        if nframes is None:
            nframes = -1

        w = wave.open(filename, "w")
        w.setparams((nchannels, sampwidth, framerate, nframes, "NONE", "not compressed"))

        max_amplitude = float(int((2 ** (sampwidth * 8)) / 2) - 1)

        for chunk in self.grouper(bufsize, samples):
            frames = b''.join(struct.pack('h', int(max_amplitude * sample)) for sample in chunk if sample is not None)
            w.writeframesraw(frames)

        w.close()
