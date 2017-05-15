import os
import time
from datetime import datetime


class Messanger(object):
    def __init__(self, queue):
        self._queue = queue
        self._resources = None

    def wait_for_resource(self, timeout=10, silent=True):
        # The resources could be already setup for this process
        if self._resources is not None:
            return self._resources

        # If not, talk to the server and wait for resources to become available
        self._queue.put(Request(os.getpid()))
        start_time = datetime.utcnow()
        while True:
            entry = self._queue.get()
            if isinstance(entry, Entry) and entry.pid == os.getpid():
                self._resources = entry.initiator(**entry.initiator_kwargs)
                return self._resources
            else:
                # If this is not my entry - ignore it and sleep for a while
                self._queue.put(entry)
                if (datetime.utcnow() - start_time).seconds > timeout:
                    if silent:
                        return
                    else:
                        raise BaseException("timedout...")
                time.sleep(0.1)


class Entry(object):
    def __init__(self, pid, initiator, initiator_kwargs):
        self._pid = pid
        self._initiator = initiator
        self._initiator_kwargs = initiator_kwargs

    @property
    def initiator(self):
        return self._initiator

    @property
    def initiator_kwargs(self):
        return self._initiator_kwargs

    @property
    def pid(self):
        return self._pid


class Request(object):
    def __init__(self, pid):
        self._pid = pid

    @property
    def pid(self):
        return self._pid


class Done(object):
    def __init__(self, pid):
        self._pid = pid

    @property
    def pid(self):
        return self._pid