import os
import re
import sys
from queue import Empty, Queue
from subprocess import PIPE, check_call
from threading import Thread
from time import sleep

import six
from mock import MagicMock
from psutil import NoSuchProcess, Popen

from py_tools import logger
from py_tools.common import replace_bad_chars
from py_tools.concurrency import ExcToQueue
from py_tools.exceptions import StructException
from py_tools.seq import conj


class ExecutionTimeout(StructException):
    pass


class CommandExecution(StructException):
    pass


_WORD_DIVIDERS = {' ', '\t', '\r', '\n'}

_QUOTE_CHARS_DICT = {
    '\\': '\\',
    ' ': ' ',
    '"': '"',
    'r': '\r',
    'n': '\n',
    't': '\t',
}


def split_args(cmd):
    return [x.strip('"') for x in re.findall(r'"[^"]+"|[^ ]+', cmd)]


class _CommandLine:
    def __init__(self, cmd):
        pass


class Command:
    def __init__(
        self,
        cmd,
        timeout=2 * 60 * 60,
        wait=True,
        out_log=None,
        silent=False,
        separate_stdout=False,
        write_stdout=True,
        dt=10,
        track_resources=False,
        retry=3,
    ):
        """
        :param cmd: command to execute
        :param timeout: timeout in seconds
        :param wait: if set to false, the process is started asynchronously
        :param out_log: file-like object for stdout and stderr
        :param silent: suppress execution details logs
        :param separate_stdout: save stderr and stdout separately
        :param write_stdout: when false, process out will be captured but now shown in console
        :param dt: how often write log of execution and check resources
        :param track_resources: save cpu and memory usage during execution
        """
        if silent:
            self.logger = MagicMock()
        else:
            self.logger = logger

        self.cmd = cmd
        self.timeout = timeout
        self.dt = dt
        self.wait = wait
        self.out_log = out_log
        self._write_stdout = write_stdout
        self.time = 0  # total time of a process
        self.retry = retry

        self._separate_stdout = separate_stdout
        self._stdout = []
        self._stderr = []

        self.track_resources = track_resources
        self._memory_usage = []
        self._cpu_times = {}
        self._started = False
        self._finished = False

    def __repr__(self):
        return '<Command: {}>'.format(self.cmd)

    def memory_peak(self):
        if not self.track_resources:
            raise ValueError('resources was not tracked')
        if self._memory_usage:
            return max(self._memory_usage)
        else:
            return 0

    def memory_average(self):
        if not self.track_resources:
            raise ValueError('resources was not tracked')
        if self._memory_usage:
            return sum(self._memory_usage) / len(self._memory_usage)
        else:
            return 0

    def cpu_percent(self):
        if not self.track_resources:
            raise ValueError('resources was not tracked')
        if not self._finished:
            raise ValueError('not finished')
        if self.time:
            return sum(self._cpu_times.values()) / self.time
        else:
            return 0

    @staticmethod
    def safe_decode(b):
        try:
            return b.decode(errors='ignore')
        except Exception:
            return str(b)

    @staticmethod
    def _format_stdout(container, size_limit=10**4, as_list=False):
        if as_list:
            return container

        stdout_str = ''.join(container)
        extra_len = len(stdout_str) - size_limit
        if extra_len <= 0:
            return stdout_str
        return '<...{} chars skipped...>'.format(extra_len).join(
            (stdout_str[: size_limit // 2], stdout_str[-size_limit // 2 :])
        )

    def stdout(self, size_limit=10**4, as_list=False):
        return self._format_stdout(self._stdout, size_limit=size_limit, as_list=as_list)

    def stderr(self, size_limit=10**4, as_list=False):
        return self._format_stdout(self._stderr, size_limit=size_limit, as_list=as_list)

    def _popen(self, *args, **kwargs):
        e = None
        r = self.retry
        for i in range(1, r + 1):
            try:
                return Popen(*args, **kwargs)
            except PermissionError as e:
                if i != r:
                    logger.info('sleep before retry', n=i)
                    sleep(i)
        else:
            raise e

    def execute(self, raise_=True, shell=False):
        """
        :param raise_: raise an error if got non-zero return code
        :param shell: Popen(shell=shell)
        """
        cmd = self.cmd
        argv0_params = cmd.split(' ', 1)
        if len(argv0_params) == 1:
            argv0 = argv0_params[0]
            params = ''
        else:
            argv0, params = argv0_params
        assert not self._started, 'Command is already executed'
        assert cmd
        self._started = True

        self.logger.info('command execute', cmd=argv0, parameters=params)
        if not self.wait:
            return self._popen(cmd, shell=shell)

        exc_q = Queue()

        @ExcToQueue(exc_q)
        def subprocess_thread():
            p.wait()

        @ExcToQueue(exc_q)
        def stdout_thread(stream, target):
            while stream:
                o = stream.readline()
                if o:
                    o_decoded = self.safe_decode(o)
                    if self._write_stdout:
                        try:
                            sys.stdout.write(replace_bad_chars(o_decoded))
                        except:
                            sys.stdout.write("<couldn't write line to stdout>")
                    target.append(o_decoded)
                elif p.poll() is not None:
                    break

        p = self._popen(
            cmd, stdout=self.out_log or PIPE, stderr=self.out_log or PIPE, shell=shell
        )
        thread = Thread(target=subprocess_thread)  # run subprocess in this thread
        thread.start()
        if not self.out_log:
            Thread(
                target=stdout_thread, args=(p.stdout, self._stdout)
            ).start()  # capture stdout
            Thread(
                target=stdout_thread,
                args=(
                    p.stderr,
                    self._stderr if self._separate_stdout else self._stdout,
                ),
            ).start()  # capture stderr

        self.time = 0
        while self.time < self.timeout:
            thread.join(self.dt)
            if thread.is_alive():
                self.time += self.dt
                if self.track_resources:
                    # not using pid because pid can be duplicated, but psutil guarantees that hash(p) is unique
                    try:
                        for p in conj(p.children(), p):
                            v = p.cpu_times()
                            self._cpu_times[hash(p)] = v.user + v.system
                        self._memory_usage.append(
                            p.memory_info().vms
                            + sum(c.memory_info().vms for c in p.children())
                        )
                    except NoSuchProcess:
                        pass
                print('command', cmd, 'is executing for', self.time, 'seconds')
            else:
                try:
                    exc_info = exc_q.get_nowait()
                except Empty:
                    pass
                else:
                    six.reraise(*exc_info)
                ret_code = p.poll()
                self.logger.info(
                    'command finished',
                    cmd=cmd,
                    time=self.time,
                    parameters=params,
                    unit='seconds',
                    return_code=ret_code,
                )
                self._finished = True
                if ret_code and raise_:
                    raise CommandExecution(
                        argv0,
                        parameters=params,
                        ret_code=ret_code,
                        stdout=self.stdout(),
                    )
                return self
        else:
            self.logger.info(
                'command timed out', cmd=cmd, time=self.timeout, unit='seconds'
            )
            p.terminate()
            thread.join()
            self._finished = True
            raise ExecutionTimeout(
                argv0, parameters=params, timeout=self.timeout, stdout=self.stdout()
            )


class DockerCommand(Command):
    USER = ''
    PASSWD = ''

    def __init__(self, img, cmd, user=None, passwd=None, **kwargs):
        super().__init__(cmd, **kwargs)
        self.img = img
        self.user = user
        self.passwd = passwd

    def _popen(self, *args, **kwargs):
        img = self.img
        assert len(args) == 1
        cmd = args[0]

        c_login = 'docker login --username {} --password {} {}'.format(
            self.user or self.USER, self.passwd or self.PASSWD, img
        )
        c_pull = 'docker pull {}'.format(img)
        c_run = 'docker run -v {mnt_src}:{mnt_dst} -w {wd} {img} {cmd}'.format(
            mnt_src=os.getcwd(), mnt_dst='/wd', wd='/wd', img=img, cmd=cmd
        )
        check_call(c_login, shell=True)
        check_call(c_pull, shell=True)
        return Popen(
            c_run, shell=True, stdout=self.out_log or PIPE, stderr=self.out_log or PIPE
        )
