import sys
import os
import tempfile
sys.path.insert(0, os.getcwd())
from data.store import Store, decrypt
import pytest
import data.store


def _create_store():
    store = Store(
        [{"this": "that", "that": "foo"},
         {"this": "that", "that": "bar"},
         {"this": "that", "that": "baz"},
         {"this": "foo", "that": "this"},
         {"this": "bar", "that": "this"},
         {"this": "baz", "that": "this"}])
    return store


def test_add_record_is_thread_safe():
    """Come to think of it...The GIL makes this never fail"""
    from multiprocessing import Process

    store = _create_store()

    def add_delete():
        for x in xrange(10):
            sx = str(x)
            record = store.add_record({"name": sx, "email": "{}@example.com".format(sx)})
            store.del_record(record)

    procs = [Process(target=add_delete) for x in xrange(10)]
    [process.start() for process in procs]
    [process.join() for process in procs]
    assert len(store) == 6


def test_persist_is_thread_safe():
    """Now, this I think could fail"""
    from threading import Thread

    store = _create_store()

    class Task(Thread):
        def run(self):
            for x in xrange(10):
                sx = str(x)
                record = store.add_record({"name": sx, "email": sx})
                store.persist("tmp.db")
                store.del_record(record)
                store.persist("tmp.db")

    tasks = [Task() for x in xrange(10)]
    [task.start() for task in tasks]
    [task.join() for task in tasks]
    store2 = data.store.load("tmp.db")
    assert store == store2


def test_Store_returns_empty_store():
    store = Store()
    assert len(store) == 0


def test_Store_constructor_accepts_a_list_of_dicts_to_initialize():
    store = Store([{}, {}])
    assert len(store) == 2


def test_Store_constructor_adds__id_field_to_each_record():
    store = Store([{}, {}])
    for record in store:
        assert "_id" in record


def test_Store_dot_sort_returns_a_sorted_store():
    store = _create_store()
    srted = store.sort("this")
    assert isinstance(srted, Store)
    assert srted[0]["this"] == "bar"


def test_Store_dot_filter_returns_new_store_with_matching_records_removed():
    store = _create_store()
    filtered = store.filter({"this": "bar"})
    assert len(filtered) == (len(store) - 1)
    assert len(filtered.find({"this": "bar"})) == 0


def test_Store_dot_group_by_returns_a_dict_of_Stores_grouped_by_field():
    store = _create_store()
    groups = store.group_by("this")
    assert len(groups.keys()) == 4
    for key, store in groups.items():
        assert isinstance(store, Store)
        for record in store:
            assert record["this"] == key


def test_find_accepts_argument_to_encrypt_fields():
    store = _create_store()
    results = store.find({}, encrypt_list=["this"], password="password")
    assert isinstance(results, Store)
    for index, record in enumerate(results):
        assert record["this"] != store[index]["this"]
        assert decrypt(record["this"], key="password") == store[index]["this"]


def test_find_one_accepts_argument_to_encrypt_fields():
    store = _create_store()
    record = store.find_one(
        {"that": "foo"},
        encrypt_list=["this"],
        password="password")
    assert record["this"] != store.find_one({"that": "foo"})["this"]
    assert decrypt(record["this"], key="password") == store.find_one({"that": "foo"})["this"]


def test_add_record_adds_a_record():
    store = Store()

    store.add_record({"this": "that", "that": "foo"})
    assert len(store) == 1


def test_del_record_removes_a_record():
    store = Store()

    store.add_record({"this": "that", "that": "foo"})
    assert len(store) == 1
    store.del_record({"this": "that", "that": "foo"})
    assert len(store) == 0


def test_del_record_raises_ValueError_if_record_doesnt_exist():
    store = _create_store()
    with pytest.raises(ValueError):
        store.del_record({"_id": 1})


def test_del_records_removes_all_matching_records():
    store = _create_store()

    assert len(store) == 6
    store.del_records({"this": "that"})
    assert len(store) == 3
    store.del_records({"this": "foo"})
    assert len(store) == 2


def test_find_one_only_returns_one_record():
    store = _create_store()

    result = store.find_one({"this": "that"})
    assert isinstance(result, dict)


def test_find_returns_list_of_matching_records():
    store = _create_store()

    result = store.find({"this": "that"})
    assert len(result) == 3


def test_find_and_find_one_accept_a_callable_as_a_matching_value():
    store = _create_store()
    results = store.find({
        "this": lambda x: x.startswith("t")
    })
    assert len(results) == 3
    result = store.find({
        "this": lambda x: x.startswith("t")
    })
    assert len([result]) == 1


def test_find_and_find_one_accept_sanitize_list_argument_and_sanitizes_those_fields():
    store = _create_store()
    results = store.find(
        {"this": "that"},
        sanitize_list=["this"])
    print "RESULTS: ", results
    print "STORE:", store
    for result in results:
        assert result["this"] == "*" * 8
    result = store.find_one(
        {"this": "that"},
        sanitize_list=["this"])
    print "RESULT:", result
    assert result["this"] == "*" * 8


def test_persist_will_persist_to_file_and_can_be_read_by_load():
    filename = os.path.join(tempfile.gettempdir(), "testdb")
    store = _create_store()
    store.persist(filename)
    store2 = data.store.load(filename)
    assert store == store2


def test_persist_will_accept_a_password_to_encrypt_the_store():
    store = _create_store()
    store.persist("test.db", password="password")
    with pytest.raises(KeyError):
        store2 = data.store.load("test.db")
    store3 = data.store.load("test.db", password="password")
    assert store3 == store


def test_sort_works_based_on_key():
    store = _create_store()
    results = store.find({}, order_by="this")
    assert results[0]["this"] == "bar"


def test_find_and_find_one_accept_compiled_regex():
    import re
    store = _create_store()
    regex = re.compile("t.*")
    results = store.find({"this": regex})
    result = [store.find_one({"this": regex})]
    assert len(results) == 3
    assert len(result) == 1


def test_each_record_gets_uuid():
    store = data.store.Store()
    store.add_record({"this": "that"})
    rec = store.find_one({"this": "that"})
    assert "_id" in rec
