import sys, os
import json
import tempfile
from bottle import request, tob
import bottle
from io import BytesIO
sys.path.insert(0, os.getcwd())
from data_store import Store
import data_store

def _create_store():
    store = Store()
    store.add_record({"this": "that", "that": "foo"})
    store.add_record({"this": "that", "that": "bar"})
    store.add_record({"this": "that", "that": "baz"})

    store.add_record({"this": "foo", "that": "this"})
    store.add_record({"this": "bar", "that": "this"})
    store.add_record({"this": "baz", "that": "this"})
    return store

def test_Store_returns_empty_store():
    store = Store()
    assert len(store) == 0

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

def test_persist_will_persist_to_file_and_can_be_read_by_load():
    filename = os.path.join(tempfile.gettempdir(), "testdb")
    store = _create_store()
    store.persist(filename)
    store2 = data_store.load(filename)
    assert store == store2

def test_add_to_global_stores_adds_store():
    store = _create_store()
    assert len(data_store.GLOBAL_STORES) == 0
    data_store.add_to_global_stores("test", store)
    assert len(data_store.GLOBAL_STORES) == 1

def test_remove_from_global_stores_removes_store():
    store = _create_store()
    data_store.add_to_global_stores("test", store)
    assert len(data_store.GLOBAL_STORES) == 1
    data_store.remove_from_global_stores("test")
    assert len(data_store.GLOBAL_STORES) == 0

def test_persist_global_stores_creates_a_file_which_load_global_stores_can_read():
    filename = os.path.join(tempfile.gettempdir(), "testglobstore")
    store = _create_store()
    data_store.add_to_global_stores("test", store)
    assert len(data_store.GLOBAL_STORES) == 1
    data_store.add_to_global_stores("test2", store)
    assert len(data_store.GLOBAL_STORES) == 2
    data_store.persist_global_stores(filename)
    data_store.GLOBAL_STORES = {}
    assert len(data_store.GLOBAL_STORES) == 0
    data_store.load_global_stores(filename)
    assert len(data_store.GLOBAL_STORES) == 2

def test_sort_works_based_on_key():
    store = _create_store()
    _results = store.find({})
    results = _results.order_by("this")
    assert _results.order_by("this")[0]["this"] == "bar"

def test_find_and_find_one_accept_compiled_regex():
    import re
    store = _create_store()
    regex = re.compile("t.*")
    results = store.find({"this": regex})
    result = [store.find_one({"this": regex})]
    assert len(results) == 3
    assert len(result) == 1

# API TESTS

def test_api_stores_get_returns_names_of_stores():
    body="name=test2"
    request.environ['CONTENT_LENGTH'] = str(len(tob(body)))
    request.environ['wsgi.input'] = BytesIO()
    request.environ['wsgi.input'].write(tob(body))
    request.environ['wsgi.input'].seek(0)
    resp = data_store.get_stores()
    assert len(json.loads(resp)) == 2
    
# TODO: IMPORTANT: The next two methods depend upon each
# other. This is bad design in unit tests, and needs to be
# fixed.
def test_api_stores_post_creates_new_store_in_global_stores():
    assert len(data_store.GLOBAL_STORES) == 2
    body="name=test3"
    request.environ['CONTENT_LENGTH'] = str(len(tob(body)))
    request.environ['wsgi.input'] = BytesIO()
    request.environ['wsgi.input'].write(tob(body))
    request.environ['wsgi.input'].seek(0)
    resp = data_store.post_stores()
    assert len(json.loads(resp)) == 0
    assert resp == "[]"
    assert len(data_store.GLOBAL_STORES) == 3

def test_api_stores_delete_deletes_store_from_global_stores():
    assert len(data_store.GLOBAL_STORES) == 3
    body="name=test3"
    request.environ['CONTENT_LENGTH'] = str(len(tob(body)))
    request.environ['wsgi.input'] = BytesIO()
    request.environ['wsgi.input'].write(tob(body))
    request.environ['wsgi.input'].seek(0)
    resp = data_store.delete_store()
    assert len(data_store.GLOBAL_STORES) == 2
    
def test_api_stores_store_get_gets_one_or_more_records():
    body = '{"name": "test2"}'
    request.environ['CONTENT_LENGTH'] = str(len(tob(body)))
    request.environ['wsgi.input'] = BytesIO()
    request.environ['wsgi.input'].write(tob(body))
    request.environ['wsgi.input'].seek(0)
    resp = data_store.get_record("test2")
    assert len(json.loads(resp)) == 5

def test_api_stores_store_post_adds_a_record():
    body = '{"this": "that", "that": "foo"}'
    request.environ["bottle.request"] = bottle.LocalRequest()
    request.environ["REQUEST_METHOD"] = "POST"
    request.environ['CONTENT_LENGTH'] = str(len(tob(body)))
    request.environ['CONTENT_TYPE'] = "application/json"
    request.environ['QUERY_STRING'] = "persist=true&filename=testglob2"
    request.environ['wsgi.input'] = BytesIO()
    request.environ['wsgi.input'].write(tob(body))
    request.environ['wsgi.input'].seek(0)
    resp = data_store.post_record("test2")
    assert len(json.loads(data_store.get_record("test2"))) == 6

def test_api_stores_store_delete_deletes_record():
    assert len(json.loads(data_store.get_record("test2"))) == 6
    body = 'desc={"this": "that"}&limit=1'
    request.environ["bottle.request"] = bottle.LocalRequest()
    request.environ["REQUEST_METHOD"] = "DELETE"
    request.environ['CONTENT_LENGTH'] = str(len(tob(body)))
    request.environ['wsgi.input'] = BytesIO()
    request.environ['wsgi.input'].write(tob(body))
    request.environ['wsgi.input'].seek(0)
    resp = data_store.delete_record("test2")
    assert len(json.loads(data_store.get_record("test2"))) == 5    

def test_api_stores_store_delete_deletes_multiple_records():
    assert len(json.loads(data_store.get_record("test2"))) == 5
    body = 'desc={"this": "that"}'
    request.environ["bottle.request"] = bottle.LocalRequest()
    request.environ["REQUEST_METHOD"] = "DELETE"
    request.environ['CONTENT_LENGTH'] = str(len(tob(body)))
    request.environ['wsgi.input'] = BytesIO()
    request.environ['wsgi.input'].write(tob(body))
    request.environ['wsgi.input'].seek(0)
    resp = data_store.delete_record("test2")
    assert len(json.loads(data_store.get_record("test2"))) == 3
    
def test_api_stores_store_put_modifies_record():
    assert len(json.loads(data_store.get_record("test2"))) == 3
    body = 'desc={"that": "foo"}&body={"this": "forever", "that": "isnt"}'
    request.environ["bottle.request"] = bottle.LocalRequest()
    request.environ["REQUEST_METHOD"] = "PUT"
    request.environ['CONTENT_LENGTH'] = str(len(tob(body)))
    request.environ['wsgi.input'] = BytesIO()
    request.environ['wsgi.input'].write(tob(body))
    request.environ['wsgi.input'].seek(0)
    resp = data_store.put_record("test2")
    assert len(json.loads(data_store.get_record("test2"))) == 3
    assert data_store.GLOBAL_STORES["test2"].find({"that": "foo"}) == []

def test_each_record_gets_uuid():
    store = data_store.Store()
    store.add_record({"this": "that"})
    rec = store.find_one({"this": "that"})
    assert "_id" in rec
