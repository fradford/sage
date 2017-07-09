import math
import struct
import wave

from functools import reduce
from PIL import Image
from tqdm import tqdm


class ImageToSound:
    def __init__(self, args):
        self.args = args
        self.total_pixels = 0
        self.total_frames = self.args.framerate * self.args.duration

    def run(self):
        img = Image.open(self.args.infile)
        self.total_pixels = reduce(lambda x, y: x * y, img.size)

        self.write_wavefile(self.args.outfile, img, self.args.chunk_size, self.args.framerate * self.args.duration,
                            framerate=self.args.framerate)

    def write_wavefile(self, filename, img, bufsize, nframes=-1, nchannels=1, sampwidth=2, framerate=44100):
        wavefile = wave.open(filename, "w")
        wavefile.setparams((nchannels, sampwidth, framerate, nframes, "NONE", "not compressed"))

        max_amplitude = 32767

        frames = b''.join(struct.pack('h', int(max_amplitude * sample)) for sample in
                          self.compute_channel(self.freq_from_file(img), bufsize))
        wavefile.writeframesraw(frames)

        wavefile.close()

    def freq_from_file(self, img):
        for pixel in tqdm((x for x in img.getdata()), total=self.total_pixels, desc="Converting Image",
                          dynamic_ncols=True, leave=False):
            cur_freq = 0
            for band in pixel:
                cur_freq += band
            yield self.sine_wave_gen(cur_freq, self.args.framerate, self.args.duration)

    @staticmethod
    def sine_wave_gen(frequency, framerate=44100, duration=1, amplitude=1):
        for i in range(framerate * duration):
            yield math.sin(2.0 * math.pi * float(frequency) * (float(i) / float(framerate))) * float(amplitude)

    @staticmethod
    def chunk_channels(channels, chunk_size):
        for iterator in channels:
            yield zip(*[iter(iterator)] * chunk_size)

    def compute_channel(self, channels, bufsize):
        # Unpacking the generator returned from chunk_channels is not only incredibly slow it also creates a temporary
        # tuple of all the objects in the generator, effectively defeating the whole purpose of using generators in the
        # first place. This is where the memory issues are coming from, this generator cannot be unpacked, it is simply
        # too large.
        for chunk in tqdm(((x for x in y) for y in zip(*self.chunk_channels(channels, bufsize))), total=self.total_frames,
                          desc="Combining Waves", dynamic_ncols=True, leave=True):
            for gen in ((x for x in y) for y in zip(*chunk)):
                yield sum(gen) / (self.total_frames * self.total_pixels)