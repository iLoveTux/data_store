import requests
from store import Store


class Client(object):
    def __init__(self, host, port):
        self.base_url = "http://{}:{}/collections".format(host, port)

    def get_collections(self):
        return requests.get(self.base_url).json()

    def create_collection(self, name):
        url = "{}/{}".format(self.base_url, name)
        return requests.post(url).json()

    def del_collection(self, name):
        url = "{}/{}".format(self.base_url, name)
        return requests.delete(url).json()

    def add_record(self, collection, record):
        url = "{}/{}/records".format(self.base_url, collection)
        return requests.post(url, json=record).json()

    def get_records(self, collection, desc):
        url = "{}/{}/records".format(self.base_url, collection)
        return Store(requests.get(url, params=desc).json())

    def del_record(self, collection, desc):
        url = "{}/{}/records".format(self.base_url, collection)
        requests.delete(url, params=desc).json()

    def update_record(self, collection, _id, updates):
        url = "{}/{}/records/{}".format(self.base_url, collection, _id)
        return requests.put(url, json=updates).json()
