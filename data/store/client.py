import requests


class Client(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def get_collections(self):
        url = "http://{}:{}/collections".format(self.host, str(self.port))
        return requests.get(url).json()
