import json
import bottle
import data.store

api = bottle.Bottle(__name__)

collections = {}

@api.route("/collections")
def get_collections():
    """Returns a list of collections."""
    global collections
    return collections

@api.route("/collections/<collection>", method="POST")
def post_collection(collection):
    """Creates a collection"""
    global collections
    new_collection = data.store.Store()
    collections[collection] = new_collection
    return new_collection

@api.route("/collections/<collection>", method="DELETE")
def del_collection(collection):
    """Deletes a collection"""
    if collection not in collections:
        bottle.abort(404)
    del collections[collection]
    
@api.route("/collections/<collection>/records", method="POST")
def post_record(collection):
    """Adds a record to collection"""
    if collection not in collections:
        bottle.abort(404)
    record = bottle.request.json
    collections[collection].add_record(record)

@api.route("/collections/<collection>/records")
def get_records(collection):
    """Search collection for records"""
    if collection not in collections:
        bottle.abort(404)
    desc = bottle.request.query
    return collections[collection].find(desc)

@api.route("/collections/<collection>/records", method="DELETE")
def delete_record(collection):
    """Delete a record from collection. A ValueError
    will be raised if there are more than one matching
    record"""
    if collection not in collections:
        bottle.abort(404)
    desc = bottle.request.query
    records = collections[collection].del_record(desc)
    return records
    
@api.route("/collections/<collection>/records/_id", method="PUT")
def update_record(collection, _id=None):
    """Updates a record with _id in collection."""
    if collection not in collections:
        bottle.abort(404)
    if _id is None:
        bottle.abort(404)

    record = collections[collection].find({"_id": _id})
    if len(record) != 1:
        bottle.abort(404)

    record = record[0]
    body = json.loads(bottle.request.body.read())
    for key, value in body.items():
        record[key] = value
    collections[collection].del_record({"_id": _id})
    collections[collection].add_record(record)
    return record
