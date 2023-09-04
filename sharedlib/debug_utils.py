import functools
import logging
import time

log=logging.getLogger(__name__)

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


def to_list(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return list(fn(*args, **kwargs))

    return wrapper


def print_memory_usage(fn):
    import psutil

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)

        log.debug('------------------------------------')

        # Get the virtual memory usage statistics
        virtual_memory = psutil.virtual_memory()

        log.debug('Virtual Memory Usage:')
        log.debug(f'Total: {virtual_memory.total / (1024 ** 2):.2f} MB')
        log.debug(f'Available: {virtual_memory.available / (1024 ** 2):.2f} MB')
        log.debug(f'Used: {virtual_memory.used / (1024 ** 2):.2f} MB')
        log.debug(f'Percent Used: {virtual_memory.percent}%')

        # Get the swap memory usage statistics
        # swap_memory = psutil.swap_memory()
        #
        # log.debug('\nSwap Memory Usage:')
        # log.debug(f'Total: {swap_memory.total / (1024 ** 2):.2f} MB')
        # log.debug(f'Used: {swap_memory.used / (1024 ** 2):.2f} MB')
        # log.debug(f'Free: {swap_memory.free / (1024 ** 2):.2f} MB')
        # log.debug(f'Percent Used: {swap_memory.percent}%')

        # Get the memory usage of the current process
        process = psutil.Process()
        process_memory = process.memory_info()

        log.debug('Current Process Memory Usage:')
        log.debug(f'RSS (Resident Set Size): {process_memory.rss / (1024 ** 2):.2f} MB')
        log.debug(f'VMS (Virtual Memory Size): {process_memory.vms / (1024 ** 2):.2f} MB')

        return result

    return wrapper
