import math
import struct

from PIL import Image
from tqdm import tqdm

import sage


class SoundToImage:
    def __init__(self, args):
        self.args = args
        self.data = []
        self.pixels = []

    def run(self):
        with sage.Timer.Timer() as timer:
            self.read_file()
            self.calc_pixels()
            self.write_image()
        print("Conversion Complete, total time: " + timer.elapsed)

    def read_file(self):
        with open(self.args.infile, 'rb') as f:
            for piece in tqdm(self.read_in_chunks(f), desc="Reading data", dynamic_ncols=True):
                self.data.append(struct.unpack("h", piece)[0]/32762)

    @staticmethod
    def read_in_chunks(file, chunk_size=2):
        while True:
            data = file.read(chunk_size)
            if not len(data) == chunk_size:
                break
            yield data

    def calc_pixels(self):
        rgba = []
        for index, i in enumerate(tqdm(self.data, desc="Calculating pixels", dynamic_ncols=True)):
            if abs(i) < 1:
                rgba.append(round(math.degrees(math.asin(i))))
            if len(rgba) == 3:
                self.pixels.append(tuple(rgba))
                rgba = []

    def write_image(self):
        size = round(math.sqrt(len(self.pixels)))
        image = Image.new("RGBA", (size, size))
        pix = image.load()
        width, height = image.size
        cur_pixel = 0
        for x in range(height):
            for y in range(width):
                pix[x, y] = self.pixels[cur_pixel]
                cur_pixel += 1

        image.save(self.args.outfile)
