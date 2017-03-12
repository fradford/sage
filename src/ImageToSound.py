import math
import sqlite3
import struct
import wave

from PIL import Image
from tqdm import tqdm

from Timer import Timer


class ImageToSound:
    def __init__(self, args):
        self.args = args
        self.sqlite_db = sqlite3.Connection("")

    def run(self):
        self.init_db(self.args.disk_db)
        print("Database initialized. Beginning conversion.")

        with Timer() as timer:
            with tqdm(total=3, desc="Total Progress", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} steps completed",
                      dynamic_ncols=True, leave=False) as total_prog:
                num_waves = self.freq_from_file(self.args.infile, self.args.note_length, self.args.all_pixels,
                                                self.args.framerate)
                total_prog.update()
                self.compute_channel(num_waves)
                total_prog.update()
                self.write_wavefile(self.args.outfile, num_waves,
                                    nframes=int(round((self.args.framerate * self.args.note_length) * num_waves)),
                                    framerate=self.args.framerate)
                total_prog.update()
        print("Conversion Complete, total time: " + timer.elapsed)

    @staticmethod
    def connect_db(disk_db=False):
        if disk_db:
            rv = sqlite3.connect("../db/waves.db")
        else:
            rv = sqlite3.connect(":memory:")
        rv.row_factory = sqlite3.Row
        return rv

    def get_db(self, disk_db=False):
        if not hasattr(self, "sqlite_db"):
            self.sqlite_db = self.connect_db(disk_db)
        return self.sqlite_db

    def close_db(self):
        if hasattr(self, "sqlite_db"):
            self.sqlite_db.close()

    def init_db(self, disk_db=False):
        db = self.get_db(disk_db)
        with open("../db/setup.sql", mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

    @staticmethod
    def grouper(iterable):
        return zip(*iterable)

    @staticmethod
    def round_freq(frequency):
        notes = [261.626, 277.183, 293.665, 311.127, 329.628, 349.228, 369.994,
                 391.995, 415.305, 440, 466.164, 493.883, 523.251, 554.365, 587.33,
                 622.254, 659.255, 698.456, 739.989, 783.991, 830.609, 880, 932.328,
                 987.767]
        for i in notes:
            if i < frequency:
                pass
            else:
                return i
        return notes[-1:][0]

    def freq_from_file(self, file, note_length, all_pixels, framerate=44100):
        freq_list = []

        img = Image.open(file)
        height = img.height
        width = img.width

        for i in range(0, height):
            r_avg, g_avg, b_avg, a_avg = 0, 0, 0, 0
            for j in range(0, width):
                try:
                    r, g, b, a = img.getpixel((j, i))
                    if all_pixels:
                        freq_list.append(self.round_freq(r + g + b + a))
                    else:
                        r_avg += r
                        g_avg += g
                        b_avg += b
                        a_avg += a
                except ValueError:
                    r, g, b = img.getpixel((j, i))
                    if all_pixels:
                        freq_list.append(self.round_freq(r + g + b))
                    else:
                        r_avg += r
                        g_avg += g
                        b_avg += b
            r_avg /= width
            g_avg /= width
            b_avg /= width
            try:
                a_avg /= width
                freq_list.append(self.round_freq(r_avg + g_avg + b_avg + a_avg))
            except NameError:
                freq_list.append(self.round_freq(r_avg + g_avg + b_avg))

        db = self.get_db()
        for index, i in enumerate(tqdm(freq_list, desc="Creating waves", dynamic_ncols=True)):
            db.execute("INSERT INTO waves (wave) VALUES (?)",
                       (str(self.sine_wave(i, framerate=framerate, note_length=note_length)),))
        db.commit()

        return len(freq_list)

    @staticmethod
    def sine_wave(frequency, framerate=44100, amplitude=1, note_length=1):
        data = []
        if amplitude > 1.0:
            amplitude = 1.0
        if amplitude < 0.0:
            amplitude = 0.0
        for i in range(0, round(note_length * framerate)):
            sine = math.sin(2.0 * math.pi * float(frequency) *
                            (float(i) / float(framerate))) * float(amplitude)
            data.append(sine)

        return data

    @staticmethod
    def smooth(wave_data):
        points = []

        def above(data):
            for i in range(len(data) - 1, 0, -1):
                if data[i] < 0:
                    return data[:i]

        def below(data):
            for i in range(len(data) - 1, 0, -1):
                if data[i] > 0:
                    return data[:i]

        if wave_data[-1:][0] < 0:
            points.extend(above(below(wave_data)))
        elif wave_data[-1:][0] > 0:
            points.extend(above(wave_data))

        for index in range(len(points)):
            points[index] /= 2
        return points

    def compute_channel(self, num_waves):
        max_waves = 100
        count = 0
        db = self.get_db()
        with tqdm(total=num_waves, desc="Smoothing waves", dynamic_ncols=True) as bar:
            while max_waves * count < num_waves:
                for row in db.execute("SELECT wave FROM waves ORDER BY id LIMIT ? OFFSET ?",
                                      (max_waves, max_waves * count)):
                    row = eval(row[0])
                    db.execute("INSERT INTO channels (channel) VALUES (?)", (str(self.smooth(row)),))
                    bar.update()
                count += 1

        db.commit()

    def write_wavefile(self, file, num_waves, nframes=0, nchannels=2, sampwidth=2, framerate=44100):
        w = wave.open(file, "wb")
        w.setparams((nchannels, sampwidth, framerate, nframes,
                     "NONE", "not compressed"))
        max_amplitude = float(int((2 ** (sampwidth * 8)) / 2) - 1)

        count = 0
        db = self.get_db()
        with tqdm(total=nframes, desc="Writing to output file", dynamic_ncols=True, leave=False) as bar:
            while count < num_waves:
                for chunk in db.execute("SELECT channel FROM channels ORDER BY id LIMIT ? OFFSET ?", (1, count)):
                    samples = (eval(chunk[0]), eval(chunk[0]))
                    count += 1
                    for index, channels in enumerate(self.grouper(samples)):
                        frames = b''.join(struct.pack('h',
                                                      int(max_amplitude * sample)) for sample in channels)
                        w.writeframesraw(frames)
                        bar.update()
        w.close()

        db.commit()
        self.close_db()
