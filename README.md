# data_store

a simple mongo-esque data_store.

## Goals

1. Provide an easy-to-use data persistence framework
2. Use python built-ins whenever possible
3. Provide features which help our users without getting in the way
4. Provide an optional REST API 

## Installation

Simply run

    $ pip install data.store

or stay up to date by downloading and building yourself

    $ cd /tmp
    $ wget https://github.com/iLoveTux/data_store/archive/master.zip
    $ unzip master.zip
    $ cd data_store-master/
    $ py.test --doctest-modules --ignore=setup.py  # optionally run the tests
    $ python setup.py install

## Basic Usage

I will go over some of the basic usage here, but if you wish to find more 
detailed documentation please check out my shared IPython Notebooks on 
wakari: https://wakari.io/sharing/bundle/ilovetux/data.store%20documentation

so, let's check out how to create a basic store, add data to it and 
search that data.

```python
import data.store

# Instanciate a Store with four records
store = data.store.Store([
    {"name": "John Doe", "email": "john@doe.com"},
    {"name": "Jim Doe", "email": "jim@doe.com"},
    {"name": "Robert Doe", "email": "robert@doe.com"},
    {"name": "Melissa Doe", "email": "melissa@doe.com"}
])

# Find based on value
results = store.find({"name": "John Doe"})  # One record

# Find based on value and sort by name
results = store.find({"name": "John Doe"}, order_by="name")  # One record

# Find based on regex
import re
regex = re.compile(r"j.*?@\w+\.com")
results = store.find({"email": regex}) # Two records

# Filter records based on value
results = store.filter({"name": "John Doe"})

# Filter records based on callable
results = store.filter({"email": lambda x: x.startswith("r")})

# Filter records based on regex
import re
regex = re.compile(r"j.*?@\w+\.com")
results = store.filter({"email": regex})

# Find based on regex and sort based on email
results = store.find({"email": regex}, order_by="email")

# limiting to one result
results = store.find_one({"email": regex}) # One Records

# find based on callable
results = store.find({"email": lambda x: x.startswith("r")})  # One Record

# Sort a store by email
srtd = store.sort(by="email")

# Group by field
groups = store.group_by("name")

# Add a record
store.add_record({"name": "ilovetux", "email": "me@ilovetux.com"})

# Delete a record based on value
store.del_record({"name": "Melissa Doe"})  # Deletes one record

# Delete multiple records based on callable
store.del_records({"name": lambda x: x.startswith("J")})

# Persist the store
store.persist("/var/data/users.db")

# Load a persisted store
store2 = data.store.load("/var/data/users.db")

# Persist the store encrypted with a password
store.persist("/var/data/users.db", password="password")

# Load an encrypted persisted store
store2 = data.store.load("/var/data/users.db", password="password")

# Find a set of records and sanitize a field on them
store2.find(
    {"email": lambda x: x.startswith("m")},
    sanitize_list=["email"])

# Find a set of records and encrypt a field on them
store2.find(
    {"email": lambda x: x.startswith("m")},
    encrypt_list=["email"],
    password="password")

```

## The REST API

A REST API is included in the package for convenience. The
API is a WSGI application written in bottle, and supports
full CRUD operations on records and collections (or Stores
as I have been calling them).

#### Using the REST APIy

The REST API provides the following endpoints:

##### Collection endpoints

GET    -> /collections              = list all collections available

POST   -> /collections/<collection> = Creates a new collection

DELETE -> /collections/<collection> = Deletes a collection

##### Record endpoints

GET    -> /collections/<collection>/records = get a list of records
       matching the keys and values passed through the query string.

POST   -> /collections/<collection>/records = adds a record to collection

DELETE -> /collections/<collection>/records = deletes a record

PUT    -> /collections/<collection>/records/_id = Update a record

#### Deploying the REST API
Deployment is relatively easy, and could consist of the
following:

```python
from data.store.api import api

api.run(server="cherrypy")
```

or to use a different server (in this case twisted):

```python
from data.store.api import api

api.run(server="twisted")
```

then save either of these files as datastore_api.py
and run

    $ python datastore_api.py

and by default the server will listen on port 8080.

Now, This is one way to deploy it, there are others,
here are some links pointing to some documentation
about deploying WSGI applications (and bottle WSGI
applications in particular):

To see a list of available servers, check out:
http://bottlepy.org/docs/dev/deployment.html#switching-the-server-backend

or to see how to deploy it behind Apache httpd check out:
http://bottlepy.org/docs/dev/deployment.html#apache-mod-wsgi

or on google app engine:
http://bottlepy.org/docs/dev/deployment.html#google-appengine

or for some info on deploying behind a load balancer:
http://bottlepy.org/docs/dev/deployment.html#load-balancer-manual-setup

## Help and Contributions

Please feel free to open an issue here on GitHub.

Contributions in the form of source code are expected to adhere as closely as
possible to PEP 8 also any feature or bug fix needs a unit test. I will 
probably cherry pick from the pull requests, so please don't be offended
if I only implement a subset of your change.
