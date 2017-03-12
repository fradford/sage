import time


class Timer:
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, error_type, value, traceback):
        self.end = time.time()

        self.elapsed = self.end - self.start
        if self.elapsed > 3600:
            self.elapsed = str(self.elapsed / 3600) + " hours."
        elif 60 < self.elapsed < 3600:
            self.elapsed = str(self.elapsed / 60) + " minutes."
        else:
            self.elapsed = str(self.elapsed) + " seconds."
