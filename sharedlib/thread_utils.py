import concurrent.futures
import functools
import logging
import queue
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from typing import Iterable, Callable

log = logging.getLogger(__name__)


def yield_run_fn_results(run_fn, args_list, n_thread=4) -> Iterable:
    return yield_run_fn_results_by_fn_list(
        (functools.partial(run_fn, *args) for args in args_list),
        n_thread=n_thread,
    )


def yield_run_fn_results_by_fn_list(fn_list, n_thread=4) -> Iterable:
    output_queue = queue.Queue()
    end_of_queue_val = '_____END____OF_____QUEUE____'

    def _create_run_with_args_fn(_fn) -> Callable:
        def _run_with_args():
            try:
                result = _fn()
            except Exception as e:
                print(e)
                log.error(e)
                log.exception(e)
                result = None

            output_queue.put(result)

        return _run_with_args

    fn_list = (_create_run_with_args_fn(fn) for fn in fn_list)

    def _run_all_args():
        with ThreadPoolExecutor(n_thread) as executor:
            futures = [executor.submit(fn) for fn in fn_list]
            for future in concurrent.futures.as_completed(futures):
                pass
            output_queue.put(end_of_queue_val)

    Thread(target=_run_all_args).start()

    while True:
        out_val = output_queue.get()
        if out_val == end_of_queue_val:
            break
        yield out_val
