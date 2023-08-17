import functools
import time


class Timer:
    def __init__(self, name=None, n_precision=5, log_fn=print):
        self.name = name
        self.process_start = 0
        self.real_start = 0  # real = total = process + net + io
        self.n_precision = n_precision
        self.log_fn = log_fn

    def __enter__(self):
        self.start()

    def __exit__(self, *args, **kwargs):
        self.print_result()

    def start(self):
        self.process_start = time.process_time()
        self.real_start = time.time()
        return self

    @property
    def time_diff(self):
        return self.time_diff_r

    @property
    def time_diff_r(self):
        time_diff = time.time() - self.real_start
        return time_diff

    @property
    def time_diff_p(self):
        time_diff = time.process_time() - self.process_start
        return time_diff

    def _float_str(self, val) -> str:
        fmt = '{:,.' + str(self.n_precision) + 'f}'
        return fmt.format(val)

    def print_result(self):
        process_diff = self.time_diff_p
        real_diff = self.time_diff_r
        self.log_fn('{} Elapsed: process[{}] real[{}]'.format(
            '[{}] '.format(self.name) if self.name else '',
            self._float_str(process_diff),
            self._float_str(real_diff)),
        )
        return real_diff

    def measure_fn(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper
