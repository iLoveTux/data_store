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
import uuid
import pickle
from cStringIO import StringIO
from threading import RLock
import base64
from itertools import cycle, izip


def encrypt(string, key="_"):
    """Return the base64 encoded XORed version of string. This is XORed with
    key which defaults to a single underscore."""
    return base64.encodestring(
        ''.join(
            chr(ord(c) ^ ord(k)) for c, k in izip(string, cycle(key)))).strip()


def decrypt(string, key="_"):
    """Returns the base64 decoded, XORed version of string. This is XORed with
    key, which defaults to a single underscore"""
    string = base64.decodestring(string)
    return ''.join(
        chr(ord(c) ^ ord(k)) for c, k in izip(string, cycle(key))).strip()

class ResultList(list):
    pass

LOCKS = {}

class Store(list):
    def __init__(self, records=None):
        """This class is meant to be a parallel to a table in a
        traditional DataBase. It inherits from list and contains
        dicts which we call records.

        If you pass in a list of dicts then they will be used to
        initialize your store with records.

        >>> store = Store([{'this': 'that'}])
        >>> store2 = Store()
        >>> store2.add_record(store.find_one({'this': 'that'}))  #doctest: +ELLIPSIS
        {'this': 'that', '_id':...}
        >>> store == store2
        True"""
        if records:
            for record in records:
                self.add_record(record)

    def add_record(self, record):
        """This method adds a record to this Store. record should be
        a dict. There is no schema in data_store, so feel free to add
        any valid Python dict.

        Every record in data.store must have a unique value for
        the field '_id', if you don't provide one then one will
        be generated.

        This method returns the record you passed in, but
        with the '_id' field added if it wasn't present.

        >>> store = Store()
        >>> store
        []
        >>> store.add_record({'this': 'that', '_id': 'test'})
        {'this': 'that', '_id': 'test'}
        >>> store
        [{'this': 'that', '_id': 'test'}]
        """
        if "_id" not in record:
            record["_id"] = uuid.uuid4().hex
        self.append(record)
        return record

    def sort(self, by="_id"):
        """Return a sorted Store. The records in the returned Store
        will be sorted by the field named in by.

        >>> store = Store([
        ...     {"this": "b"},
        ...     {"this": "a"}])
        >>> srtd = store.sort(by="this")
        >>> print srtd[0]["this"]
        a
        """
        return self.find({}, order_by=by)

    def filter(self, desc):
        """Returns a Store where any records matching desc is removed.
        This is functionally the oposite of find.

        >>> store = Store([
        ...     {"this": "b"},
        ...     {"this": "a"}])
        >>> filtered = store.filter({"this": "a"})
        >>> print len(filtered)
        1
        >>> print filtered[0]["this"]
        b
        """
        matches = self.find(desc)
        ret = self.find({})
        for match in list(matches):
            ret.del_record({"_id": match["_id"]})
        return ret

    def group_by(self, by):
        """Returns a dict containing the values of by for the keys and
        Stores for the values where the field referenced in by matches
        the key.

        >>> store = Store([
        ...     {"this": "a"},
        ...     {"this": "a"},
        ...     {"this": "b"},
        ...     {"this": "b"},
        ...     {"this": "c"},
        ...     {"this": "c"}])
        >>> groups = store.group_by("this")
        >>> print len(groups.keys())
        3
        >>> print len(groups["a"])
        2
        """
        groups = {}
        for record in self:
            if record[by] in groups:
                groups[record[by]].append(record)
            else:
                groups[record[by]] = [record]
        for k,v in dict(groups).items():
            groups[k] = Store(v)
        return groups

    def del_record(self, desc):
        """This will delete a record from this Store matching desc
        as long as desc only matches one record, otherwise raise a
        ValueError. The record which was deleted is returned to you.

        >>> store = Store([{'_id': 'that'}])
        >>> store
        [{'_id': 'that'}]
        >>> store.del_record({'_id': 'that'})
        {'_id': 'that'}
        >>> store
        []
        """
        record = self.find_one(desc)
        records = self.find(desc)
        if [record] != records:
            raise ValueError("{} matches more than one record! Aborting...".format(str(desc)))
        if record:
            self.remove(record)
        return record

    def del_records(self, desc):
        """This acts just as del_record except that it will happily
        delete any number of records matching desc. The records which
        were deleted are returned.

        >>> store = Store([
        ...     {'this': 'that', '_id': 'test1'},
        ...     {'this': 'that', '_id': 'test2'},
        ...     {'this': 'that', '_id': 'test3'}])
        >>> store.del_records({'this': 'that'})
        [{'this': 'that', '_id': 'test1'}, {'this': 'that', '_id': 'test2'}, {'this': 'that', '_id': 'test3'}]
        """
        records = self.find(desc)
        for record in records:
            self.remove(record)
        return records

    def find_one(self, desc, sanitize_list=None, encrypt_list=None, password="_"):
        """Returns one record matching desc, if more than one record
        matches desc returns the first one.

        desc should be a dict whose keys eveluate to one of the
        following:

        1. A value which will be tested for equality against the
        value the key in each record in the store.
        2. A compiled regular expression object (ie like the
        value returned by re.compile). Each record in the store
        will be tested for a match against the regex for the value of
        key
        3. A callable which accepts one argument (the value of key in
        the current record) and returns True or False depending on
        whether the record should be included in the result set.

        If sanitize_list is specified then it must be an iterable
        which contains values which when found as a key in a record
        will sanitize the value of that field in the result set.

        >>> store = Store([
        ...     {'this': 'that', '_id': 'test1'},
        ...     {'this': 'that', '_id': 'test2'},
        ...     {'this': 'that', '_id': 'test3'}])
        >>> store.find_one({'this': 'that'})
        {'this': 'that', '_id': 'test1'}
        """
        for item in self:
            for key, value in desc.items():
                if hasattr(value, "match"):
                    if not value.match(item.get(key, None)):
                        break
                elif callable(value):
                    if not value(item[key]):
                        break
                else:
                    if not value == item[key]:
                        break
            else:
                # Needed to account for changing the actual store,
                # Rather than just sanitizing the ResultList
                _item = item.copy()
                if sanitize_list:
                    for key in sanitize_list:
                        if item.get(key, None):
                            _item[key] = "*" * 8
                if encrypt_list:
                    for field in encrypt_list:
                        if item.get(field, None):
                            _item[field] = encrypt(_item[field], key=password)
                return _item

    def find(self, desc, sanitize_list=None, encrypt_list=None, password="_", order_by=None):
        """Returns a ResultList containing records matching
        desc. If sanitize_list is specified it should be an iterable
        yielding keys of fields you would like sanitized. Those fields
        will be set to a value of '********'.

        desc should follow the same rules as defined above in the
        docstring for find_one.

        >>> store = Store([
        ...     {'this': 'that', '_id': 'test1'},
        ...     {'this': 'that', '_id': 'test2'},
        ...     {'this': 'that', '_id': 'test3'}])
        >>> store.find({'this': 'that'})
        [{'this': 'that', '_id': 'test1'}, {'this': 'that', '_id': 'test2'}, {'this': 'that', '_id': 'test3'}]
        """
        ret = ResultList()
        for item in self:
            for key, value in desc.items():
                if hasattr(value, "match"):
                    if not value.match(item.get(key, None)):
                        break
                elif callable(value):
                    if not value(item[key]):
                        break
                else:
                    if not value == item.get(key, None):
                        break
            else:
                # Needed to account for changing the actual store,
                # Rather than just sanitizing the ResultList
                ret.append(item.copy())
        for index, record in enumerate(list(ret)):
            if sanitize_list:
                for field in sanitize_list:
                    if record.get(field, None):
                        ret[index][field] = "*" * 8
            if encrypt_list:
                for field in encrypt_list:
                    if record.get(field, None):
                        ret[index][field] = encrypt(ret[index][field], key=password)
        if order_by is not None:
            ret = sorted(ret, key=lambda k: k[order_by])
        return Store(ret)

    def persist(self, filename, password=None):
        """Persist current data_store to a file named filename.
        A RLock from the threading module is used (unique by
        filename) to ensure thread safety.

        >>> store = Store([
        ...     {'this': 'that', '_id': 'test1'},
        ...     {'this': 'that', '_id': 'test2'},
        ...     {'this': 'that', '_id': 'test3'}])
        >>> store.persist("test.db")
        >>> store2 = load("test.db")
        >>> store == store2
        True
        """
        global LOCKS
        if filename not in LOCKS:
            LOCKS[filename] = RLock()
        with LOCKS[filename]:
            with open(filename, "wb") as fout:
                pickle.dump(self, fout)
            if password:
                with open(filename, "rb") as fin:
                    contents = fin.read()
                contents = encrypt(contents, key=password)
                with open(filename, "wb") as fout:
                    fout.write(contents)


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
