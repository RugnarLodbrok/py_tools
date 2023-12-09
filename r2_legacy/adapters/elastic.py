from datetime import datetime
from queue import Empty
from random import random
from threading import Thread
from time import sleep, time

from .session_keeper import http_session


class ElasticAdapter:
    SCHEMA = dict(
        mappings=dict(
            doc=dict(
                properties=dict(
                    # data=dict(type="text"),
                    # cfg=dict(type="text"),
                )
            )
        )
    )

    def __init__(
        self, index, url=None, doc_type='doc', fields=None, timestamp_int=False
    ):
        # :index example: 'my-logs-%Y-%m-%d'
        self.url = url
        self.doc_type = doc_type
        if not url:
            self.url = 'http://localhost:9200'
        self.index = index
        self._indices = set()
        self._consumer_thread = None
        self._consume_flag = False

        self._dynamic_index = '%' in index
        self.timestamp_int = timestamp_int

        if fields is None:
            fields = dict(
                timestamp=dict(
                    type='date', format='epoch_second||yy-MM-dd HH:mm:ss.SSSSSSZ'
                )
            )
        self.schema = dict(mappings={doc_type: dict(properties=fields)})

    def _epoch_to_index(self, epoch):
        if self._dynamic_index and epoch:
            return datetime.fromtimestamp(epoch).strftime(self.index)
        else:
            return self.index

    def _add_index(self, index):
        index_url = self.url + '/' + index
        for i in range(
            4
        ):  # assuming we can create index in 4 tries or find it created by another client
            if http_session.session.get(index_url).ok:
                break
            elif http_session.session.put(index_url, json=self.schema).ok:
                break
            else:
                print('clash!..')
                sleep(random() * 3)
        else:
            raise AssertionError(
                "couldn't create an elastic index in 4 tries: {}".format(index)
            )
        self._indices.add(index)

    def post(self, json, **kwargs):
        timestamp = json.get('timestamp')
        if not timestamp:
            if self.timestamp_int:
                json['timestamp'] = int(time())
            else:
                json['timestamp'] = time()
            timestamp = json.get('timestamp')
        index = self._epoch_to_index(timestamp)
        while index not in self._indices:
            self._add_index(index)
        url = self.url + '/' + index + '/' + self.doc_type
        r = http_session.session.post(
            self.url + '/' + index + '/' + self.doc_type, json=json, **kwargs
        )
        if not r.ok:
            print(url)
            from json import dumps

            print(dumps(json, indent=4))
            raise AssertionError(r.content)

    def stop_consume(self):
        if not self._consumer_thread:
            raise AssertionError('not consuming')
        self._consume_flag = False

    def consume(self, q):
        """
        posting in a thread from queue
        :param q:
        :return:
        """
        if self._consumer_thread:
            raise AssertionError('already consuming')

        def foo():
            while True:
                try:
                    v = q.get(block=False)
                except Empty:
                    if self._consume_flag:
                        sleep(1)
                    else:
                        break
                else:
                    self.post(v)

        self._consume_flag = True
        self._consumer_thread = Thread()
