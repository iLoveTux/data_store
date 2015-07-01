# -*- coding: utf-8 -*-
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
import pickle
from cStringIO import StringIO
from store import Store, decrypt


def load(filename, password=None):
    """Returns a data_store loaded from a file to which it
    was persisted

    >>> store = Store([
    ...     {'this': 'that', '_id': 'test1'},
    ...     {'this': 'that', '_id': 'test2'},
    ...     {'this': 'that', '_id': 'test3'}])
    >>> store.persist("test.db")
    >>> store2 = load("test.db")
    >>> store == store2
    True
    """
    if password:
        with open(filename, "rb") as fin:
            contents = fin.read()
            contents = decrypt(contents, key=password)
        f = StringIO()
        f.write(contents)
        f.seek(0)
        store = pickle.load(f)
    else:
        with open(filename, "rb") as fin:
            store = pickle.load(fin)
    return store

default_store = Store()

if __name__ == "__main__":
    pass
