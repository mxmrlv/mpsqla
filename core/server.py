import os
import multiprocessing

import time

from core import messaging


class Server(object):
    def __init__(self, default_initiator, base_dir, filename='db.sqlite'):
        self._initiator = default_initiator
        self._file_path = os.path.join(base_dir, filename)
        self._resources = {}
        self._queue = multiprocessing.Queue()
        self._process = None
        self._checked_out = False

    @property
    def queue(self):
        return self._queue

    def _create_and_register_resources(self, pid):
        self._resources[pid] = messaging.Entry(pid, self._initiator, dict(file_path=self._file_path))

    def get_resource(self, pid):
        if pid not in self._resources:
            self._create_and_register_resources(pid)
        self._checked_out = True
        return self._resources[pid]

    def start(self):
        self._process = multiprocessing.Process(target=self.serve)
        self._process.start()

    def serve(self):
        """
        Serves any request to the server. Orchestrates the use of engines and sessions across 
        processes. 
        :return: 
        """
        while True:
            request = self.queue.get(timeout=3)
            if isinstance(request, messaging.Request) and not self._checked_out:
                resource = self.get_resource(request.pid)
                self._queue.put(resource)
            elif isinstance(request, messaging.Done):
                self._checked_out = False
                del self._resources[request.pid]
            else:
                self.queue.put(request)
            time.sleep(0.1)

    def close(self):
        self._process.close()
