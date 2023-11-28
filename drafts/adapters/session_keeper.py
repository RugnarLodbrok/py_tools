from threading import Lock, Thread
from time import sleep, time

from requests import Session


class SessionKeeper:
    def __init__(self, session_class, timeout=600):
        self.session_class = session_class
        self.timeout = timeout
        self.lock = Lock()

        self.expire_time = time()
        self._session = None
        self.closed = True

    def _timer(self):
        while True:
            sleep(1)
            with self.lock:
                if time() >= self.expire_time:
                    print('close session')
                    self._session.close()
                    self.closed = True
                    return

    @property
    def session(self):
        self.expire_time = time() + self.timeout
        with self.lock:
            if self.closed:
                print('create session')
                self.expire_time = time() + self.timeout
                self._session = self.session_class()
                Thread(target=self._timer, daemon=True).start()
                self.closed = False
        return self._session


http_session = SessionKeeper(Session, 30)
