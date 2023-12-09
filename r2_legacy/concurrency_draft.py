import sys
from concurrent.futures import Future, ProcessPoolExecutor, ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from itertools import count
from queue import Empty, Queue
from threading import RLock, Thread
from time import sleep


class ExcInfo:
    def __init__(self, exc_type, exc_val, exc_tb):
        self.exc_type = exc_type
        self.exc_val = exc_val
        self.exc_tb = exc_tb


def _check_exception_value(v):
    if isinstance(v, tuple) and len(v) == 3 and issubclass(v[0], Exception):
        raise v[1]


class IterableQueue(Queue):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._open = True

    def close(self):
        self._open = False

    def put(self, item, block=True, timeout=None):
        if not self._open:
            raise RuntimeError('queue is closed')
        return super().put(item, block=block, timeout=timeout)

    def __iter__(self):
        while True:
            try:
                while True:
                    yield self.get(timeout=0.1)
            except Empty:
                if not self._open:
                    break


class RoundOutBuffer:
    def __init__(self, size, raise_on_error=True):
        self.lock = RLock()
        self.size = size
        self.i = 0
        self.data = [None for _ in range(size)]
        self.data_exists = [False for _ in range(size)]
        self.raise_on_error = raise_on_error
        self.set_indices = []
        self._open = 0

    def close(self):
        self._open -= 1

    def close_all(self):
        self._open = 0

    def open(self):
        self._open += 1

    def __setitem__(self, key, value):
        w = 0
        self.set_indices.append(key)
        while key - self.i >= self.size:
            if w > 10:
                print('stuck on setitem')
                raise RuntimeError(
                    'stuck on setitem\nkey: {} self.i: {}\n{}\nfree_slots:'
                    ' {}\ndata: {}:'.format(
                        key, self.i, '', self.set_indices[-20:], self.data_exists
                    )
                )
            if not self._open:
                return
            w += 1
            sleep(0.1)
        idx = key % self.size
        with self.lock:
            if not self.data_exists[idx] == False:
                print('set to occupied slot')
                raise RuntimeError('set to occupied slot')
            self.data_exists[idx] = True
            self.data[idx] = value

    def __iter__(self):
        s = self.size
        w = 0
        for i in count():
            idx = i % s
            while not self.data_exists[idx]:
                if w > 200:
                    print('stuck on iter')
                    print(self.data)
                    print(self.data_exists)
                    print('i:', i)
                    print('self.open:', self._open)
                    raise RuntimeError(
                        '\n'.join(
                            [
                                'stuck on iter',
                                str(self.data),
                                str(self.data_exists),
                                str(i),
                            ]
                        )
                    )
                if not self._open:
                    return
                w += 1
                sleep(0.1)
            with self.lock:
                v = self.data[idx]
                self.data[idx] = None
                self.data_exists[idx] = False
                self.i = i + 1
                if self.raise_on_error:
                    _check_exception_value(v)

                yield v


class WorkerThread(Thread):
    def __init__(self, f, q, res):
        """
        :param f: function
        :param q: queue with inputs
        :param res: dict with outputs
        :param input_flag: mutable flag that indicates that queue is done. Or None.
        :return:
        """
        super().__init__()
        self.q = q
        self.res = res
        self.f = f

    def run(self):
        if isinstance(self.res, RoundOutBuffer):
            self.res.open()
        try:
            for num, arg in self.q:
                if isinstance(arg, ExcInfo):
                    self.res[num] = arg
                try:
                    self.res[num] = self.f(arg)
                except Exception:
                    self.res[num] = ExcInfo(*sys.exc_info())
        finally:
            if isinstance(self.res, RoundOutBuffer):
                self.res.close()


def lazy_tmap(f, seq, pool=10, q_size=100):
    q = IterableQueue(maxsize=q_size)
    res = RoundOutBuffer(q_size)

    def filler():
        try:
            for x in enumerate(seq):
                q.put(x)
        except:
            q.put(ExcInfo(*sys.exc_info()))
        finally:
            q.close()

    Thread(target=filler, name='filler').start()
    threads = [WorkerThread(f, q, res) for _ in range(pool)]
    for t in threads:
        t.start()

    try:
        yield from res
    except Exception:
        q.close()
        res.close_all()
        raise


def thread_map(f, iterable, pool=None):
    """
    Just like [f(x) for x in iterable] but each f(x) in a separate thread.
    :param f: f
    :param iterable: iterable
    :param pool: thread pool, infinite by default
    :return: list if results
    """
    res = {}
    if pool is None:

        def target(arg, num):
            try:
                res[num] = f(arg)
            except:
                res[num] = sys.exc_info()

        threads = [
            Thread(target=target, args=[arg, i]) for i, arg in enumerate(iterable)
        ]
    else:
        queue = IterableQueue()
        for i, arg in enumerate(iterable):
            queue.put((i, arg))
        queue.close()

        threads = [WorkerThread(f, queue, res) for _ in range(pool)]

    [t.start() for t in threads]
    [t.join() for t in threads]
    return [res[i] for i in range(len(res))]


def task_queue(
    f, iterator, pool=10, on_fail=lambda _: None, result_queue=None, mode='thread'
):
    """
    future = task_queue(f, iterator, pool=5)
    try:
        while not future.done():
            try:
                future.result(.2)
            except FutureTimeoutError:
                pass
            print('\rdone {done}, in work: {delayed}  '.format(**future.stats))
            sys.stdout.flush()
    except KeyboardInterrupt:
        future.cancel()
        raise

    :param f:
    :param iterator:
    :param pool:
    :param on_fail:
    :param mode: 'thread' or 'process'
    :return:
    """
    if mode == 'thread':
        PoolExecutor = ThreadPoolExecutor
    elif mode == 'process':
        PoolExecutor = ProcessPoolExecutor
    else:
        raise ValueError('unknown mode: {}'.format(mode))

    def submit_next_job():
        try:
            obj = next(iterator)
        except StopIteration:
            return
        if future.cancelled():
            return
        stats['delayed'] += 1
        _fut = executor.submit(f, obj)
        _fut.obj = obj
        _fut.add_done_callback(done_callback)

    def done_callback(fut):
        with io_lock:
            submit_next_job()
            stats['delayed'] -= 1
            stats['done'] += 1
        if fut.exception():
            on_fail(fut.exception(), fut.obj)
        elif result_queue:
            result_queue.put(fut.result())
        if stats['delayed'] == 0:
            future.set_result(stats)

    def cleanup(_):
        with io_lock:
            executor.shutdown(wait=False)

    io_lock = RLock()
    executor = PoolExecutor(pool)
    future = Future()
    future.stats = stats = {'done': 0, 'delayed': 0}
    future.add_done_callback(cleanup)

    with io_lock:
        for _ in range(pool):
            submit_next_job()

    return future


def threaded_generator(
    f, iterator, pool=10, on_fail=lambda _: None, q_size=5000, mode='thread'
):
    result = Queue(maxsize=q_size)
    future = task_queue(
        f, iterator, pool=pool, on_fail=on_fail, result_queue=result, mode=mode
    )
    try:
        while not future.done():
            try:
                future.result(0.2)
            except FutureTimeoutError:
                pass
            while True:
                try:
                    yield result.get_nowait()
                except Empty:
                    break
    except KeyboardInterrupt:
        future.cancel()
        raise
