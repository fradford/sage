import math
import struct
import wave
from functools import reduce
from itertools import chain, islice

from PIL import Image
from tqdm import tqdm


# TODO: Parallelism


class ImageToSound:
    def __init__(self, args):
        self.args = args
        self.total_pixels = 0
        self.total_frames = self.args.framerate * self.args.duration

    def run(self):
        img = Image.open(self.args.infile)
        self.total_pixels = reduce(lambda x, y: x * y, img.size)

        self.write_file(self.args.outfile, img, self.total_frames, framerate=self.args.framerate)

    def write_file(self, filename, img, num_frames=-1, num_channels=1, sample_width=2, framerate=44100):
        file = wave.open(filename, "w")
        file.setparams((num_channels, sample_width, framerate, num_frames, "NONE", "not compressed"))

        max_amplitude = 32767

        for chunk in self.group(self.args.chunk_size, self.combine_wave(img)):
            frames = b''.join(struct.pack('h', int(max_amplitude * sample)) for sample in chunk)
            file.writeframesraw(frames)

        file.close()

    def combine_wave(self, img):
        def get_freq(rgb):
            cur_freq = 0
            for band in rgb:
                cur_freq += band
            return cur_freq

        for frame in tqdm(range(self.total_frames), desc="Calculating Wave", dynamic_ncols=True):
            value = 0
            if self.args.inner_count:
                for pixel in tqdm((x for x in img.getdata()), total=self.total_pixels, desc="Reading image",
                                  dynamic_ncols=True, leave=False):
                    value += self.next_sine_val(get_freq(pixel), frame, self.args.framerate)
            else:
                for pixel in (x for x in img.getdata()):
                    value += self.next_sine_val(get_freq(pixel), frame, self.args.framerate)
            yield value / self.total_pixels

    @staticmethod
    def next_sine_val(frequency, frame=0, framerate=44100, amplitude=1):
        return math.sin(2.0 * math.pi * float(frequency) * (float(frame) / float(framerate))) * float(amplitude)

    @staticmethod
    def group(chunk_size, iterator):
        it = iter(iterator)
        while True:
            chunk = islice(it, chunk_size)
            try:
                first = next(chunk)
            except StopIteration:
                return
            yield chain((first,), chunk)
