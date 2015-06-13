# -*- coding: utf-8 -*-
import pytest
import sys
import os
sys.path.insert(0, os.getcwd())
#import pytest
#import data.store
from data.store import client
from data.store import Store
from data.store import api
from threading import Thread
import requests
import signal
from time import sleep
import atexit


def _start_server():
    @api.api.route("/shutdown")
    def shutdown_server():
        os.kill(os.getpid(), signal.SIGTERM)
    api.api.run()

def stop_server():
    requests.get("http://127.0.0.1:8080/shutdown")


@pytest.fixture
def start_server():
    t = Thread(target=_start_server)
    t.start()
    return True


def test_client_sanity(start_server):
    c = client.Client("127.0.0.1", 8080)
    coll = c.get_collections()
    assert isinstance(coll, dict)
