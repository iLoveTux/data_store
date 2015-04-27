"""
# data_store

This module provide an easy api to a generic schema-less data_store.

## Create a Store

## Use the default_store

## Use the GLOBAL_STORE

## Adding records

## Searching

## Deleting records

## Persistence

## Load persisted data_store
"""
import os
import sys
import json
import uuid
import pickle
import bottle

class ResultSet(list):
    def order_by(self, key):
        return sorted(self, key=lambda k: k[key])

class Store(list):
    def __init__(self):
        """
        This class is meant to be a parallel to a table in a
        traditional DataBase. It inherits from list and contains
        dicts which we call records.
        """
        pass
    
    def add_record(self,record):
        """This method adds a record to this Store. record should be
        a dict. There is no schema in data_store, so feel free to add
        any valid Python dict."""
        if not hasattr(record, "_id"):
            record["_id"] = uuid.uuid4().hex
        self.append(record)
    
    def del_record(self, desc):
        """This will delete a record from this Store matching desc
        as long as desc only matches one record, otherwise raise a
        ValueError."""
        record = self.find_one(desc)
        if record:
            self.remove(record)
        return record
    
    def del_records(self, desc):
        """This acts just as del_record except that it will happily
        delete any number of records matching desc."""
        records = self.find(desc)
        for record in records:
            self.remove(record)
        return records
    
    def find_one(self, desc):
        """Returns one record matching desc, if more than one record
        matches desc returns the first one."""
        for item in self:
            for key, value in desc.items():
                if hasattr(value, "match"):
                    if not value.match(item.get(key, None)):
                        break
                else:
                    if not value == item[key]:
                        break
            else:
                return item
    
    def find(self, desc):
        """Returns all records matching desc."""
        ret = ResultSet()
        for item in self:
            for key, value in desc.items():
                if hasattr(value, "match"):
                    if not value.match(item.get(key, None)):
                        break
                else:
                    if not value == item.get(key, None):
                        break
            else:
                ret.append(item)
        return ret
    
    def persist(self, filename):
        """Persist current data_store to a file named filename"""
        with open(filename, "wb") as fout:
            pickle.dump(self, fout)
    
def load(filename):
    """Returns a data_store loaded from a file to which it
    was persisted"""
    with open(filename, "rb") as fin:
        store = pickle.load(fin)
    return store

def add_to_global_stores(name, store):
    global GLOBAL_STORES
    GLOBAL_STORES[name] = store

def remove_from_global_stores(name):
    global GLOBAL_STORES
    del GLOBAL_STORES[name]

def persist_global_stores(filename):
    global GLOBAL_STORES
    with open(filename, "wb") as fout:
        pickle.dump(GLOBAL_STORES, fout)

def load_global_stores(filename):
    global GLOBAL_STORES
    with open(filename, "rb")as fin:
        GLOBAL_STORES = pickle.load(fin)

global GLOBAL_STORES
GLOBAL_STORES = {}
global DB_PATH
DB_PATH = "/tmp"

default_store = Store()

##
#
# The API
# =======
#
# REST
#
# Each endpoint and it's purpose is listed below. The behavior of
# these endpoints can be modified through parameters passed in through
# the request. For more information on the parameters accepted at each
# endpoint please consult the endpoint's docstring.
#
# NOTE: The REST API will only work for stores in GLOBAL_STORES.
#
# Endpoint            Method            Description
# =====================================================================
# 
# /stores            GET                Return a list of stores
# /stores            POST            Create a new store
# /stores            DELETE            Deletes a store
#
# /stores/<store>     GET                Search for record(s) in store
# /stores/<store>    POST            Add a record to store
# /stores/<store>    PUT                Modify a record from store
# /stores/<store>    DELETE             Remove record(s) from store
#
# /persist            POST            Persist GLOBAL_STORES as they are
#
# =====================================================================

api = bottle.Bottle(__name__)

@api.route("/stores")
def get_stores():
    global GLOBAL_STORES
    stores = GLOBAL_STORES
    names = stores.keys()

    bottle.response.content_type = "application/json"
    return json.dumps(names)

@api.route("/stores", method="POST")
def post_stores():
    global GLOBAL_STORES
    stores = GLOBAL_STORES
    name = bottle.request.params.get("name")
    store = Store()
    add_to_global_stores(name, store)
    bottle.response.content_type = "application/json"
    return json.dumps(store)

@api.route("/stores", method="DELETE")
def delete_store():
    global GLOBAL_STORES
    stores = GLOBAL_STORES
    name = bottle.request.params.get("name")
    store = stores[name]
    remove_from_global_stores(name)
    bottle.response.content_type = "application/json"
    return json.dumps(store)

@api.route("/stores/<store>")
def get_record(store):
    """This endpoint allows searching through a store in GLOBAL_STORES.
    The following query parameters are supported (all others are
    ignored):
    
    * desc - a JSON string representing a spec with which to search
    through the records (defaults to matching all records).
    * limit - A limit on the number of records to return (defaults to
    -1 or no limit)"""
    global GLOBAL_STORES
    stores = GLOBAL_STORES
    
    # Get the description of the desired record
    desc = bottle.request.query.get("desc", default="{}")
    print desc
    desc = json.loads(desc)
    
    # Get the limit of records to return (-1 means no limit)
    limit = bottle.request.query.get("limit", default=-1, type=int)
    results = stores[store].find(desc)
    
    # For some reason bottle isn't allowing me to just return
    # the data structure for automatic conversion to JSON.This
    # is a work-around.
    bottle.response.content_type = "application/json"
    return json.dumps(results[0:limit])

@api.route("/stores/<store>",method="POST")
def post_record(store):
    global GLOBAL_STORES
    global DB_PATH
    stores = GLOBAL_STORES
    
    # Get the body of the post (should be JSON)
    body = bottle.request.json
    persist = bottle.request.query.get("persist", False)
    filename = bottle.request.query.get("filename", "globstore")
    filename = os.path.join(DB_PATH, filename)
    
    stores[store].add_record(body)
    bottle.request.content_type = "application/json"
    if persist:
        persist_global_stores(filename)
    return json.dumps(body)

@api.route("/stores/<store>", method="PUT")
def put_record(store):
    global GLOBAL_STORES
    stores = GLOBAL_STORES
    
    body = bottle.request.params.get("body")
    body = json.loads(body)
    
    desc = bottle.request.params.get("desc", default="{}")
    desc = json.loads(desc)
    
    result = stores[store].find_one(desc)
    stores[store][stores[store].index(result)] = body
    bottle.request.content_type = "application/json"
    return json.dumps(body)

@api.route("/stores/<store>", method="DELETE")
def delete_record(store):
    global GLOBAL_STORES
    stores = GLOBAL_STORES
    desc = bottle.request.params.get("desc", default="{}")
    desc = json.loads(desc)
    
    limit = bottle.request.params.get("limit", default=-1, type=int)
    results = stores[store].find(desc)
    results = results[0:limit]
    for result in results:
        stores[store].del_record(result)
    bottle.request.content_type = "application/json"
    return json.dumps(results)

@api.route("/persist", method="POST")
def persist():
    global DB_PATH
    filename = bottle.request.query.get("filename", "globstore")
    filename = os.path.join(DB_PATH, filename)
    persist_global_stores(filename)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        load_global_stores(sys.argv[1])
    api.run(host="0.0.0.0", port=4050, debug=True)
