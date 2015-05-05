import data.store
import bottle
from io import BytesIO
from data.store import api

def test_api_exists():
    assert hasattr(data.store, "api")

def test_get_collections_returns_list_of_collections():
    assert data.store.api.get_collections() == {}

def test_del_collection_deletes_a_collection():
    api.post_collection("new1")
    length = len(api.collections)
    api.del_collection("new1")
    assert (length - 1) == len(api.collections)

def test_post_to_collections_collection_creates_new_collection():
    data.store.api.post_collection("new")
    assert "new" in data.store.api.collections 

def test_post_to_post_record_adds_a_record_to_collection():
    body = '{"name": "cliff", "email": "me@ilovetux.com"}'
    bottle.request.environ['CONTENT_LENGTH'] = str(len(bottle.tob(body)))
    bottle.request.environ['CONTENT_TYPE'] = "application/json"
    bottle.request.environ['wsgi.input'] = BytesIO()
    bottle.request.environ['wsgi.input'].write(bottle.tob(body))
    bottle.request.environ['wsgi.input'].seek(0)
    api.post_record("new")
    assert "new" in data.store.api.collections
    assert len(data.store.api.collections["new"]) == 1
    
def test_get_to_get_records_returns_records():
    body = "name=cliff"
    bottle.request.environ['CONTENT_LENGTH'] = str(len(bottle.tob(body)))
    bottle.request.environ['wsgi.input'] = BytesIO()
    bottle.request.environ['wsgi.input'].write(bottle.tob(body))
    bottle.request.environ['wsgi.input'].seek(0)
    results = api.get_records("new")
    assert len(results) == 1

def test_delete_to_delete_record_deletes_a_record():
    body = "name=cliff"
    bottle.request.environ['CONTENT_LENGTH'] = str(len(bottle.tob(body)))
    bottle.request.environ['wsgi.input'] = BytesIO()
    bottle.request.environ['wsgi.input'].write(bottle.tob(body))
    bottle.request.environ['wsgi.input'].seek(0)
    results = api.delete_record("new")
    assert len(api.collections["new"]) == 0

def test_update_record_updates_a_record():
    api.collections["new"].add_record({"name": "Cliff", "_id": "test"})
    body = '{"email": "me@ilovetux.com"}'
    bottle.request.environ['CONTENT_LENGTH'] = str(len(bottle.tob(body)))
    bottle.request.environ['CONTENT_TYPE'] = "application/json"
    bottle.request.environ['wsgi.input'] = BytesIO()
    bottle.request.environ['wsgi.input'].write(bottle.tob(body))
    bottle.request.environ['wsgi.input'].seek(0)

    results = api.update_record("new", "test")
    assert api.collections["new"].find({"_id": "test"})[0]["email"] == "me@ilovetux.com"
