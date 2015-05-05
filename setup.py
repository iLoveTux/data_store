#!/usr/bin/env python

from setuptools import setup

setup(name='data.store',
      version='0.6.4',
      description='''a simple mongo-esque data_store.
Goals<br />
<br />
1. Provide an easy-to-use data persistence framework<br />
2. Use python built-ins whenever possible<br />
3. Provide features which help our users without getting in the way<br />
4. Provide an optional REST API <br />

Installation<br />
<br />
Simply run<br />
<br />
    $ pip install data.store<br />
<br />
or stay up to date by downloading and building yourself<br />
<br />
    $ cd /tmp<br />
    $ wget https://github.com/iLoveTux/data_store/archive/master.zip<br />
    $ unzip master.zip<br />
    $ cd data_store-master/<br />
    $ py.test --doctest-modules --ignore=setup.py  # optionally run the tests<br />
    $ python setup.py install<br />
<br />
Basic Usage<br />
<br />
I will go over some of the basic usage here, but if you wish to find more<br />
detailed documentation please check out my shared IPython Notebooks on<br />
wakari: https://wakari.io/sharing/bundle/ilovetux/data.store%20documentation<br />
<br />
so, let's check out how to create a basic store, add data to it and<br />
search that data.<br />

<br />
```python<br />
import data.store<br />
<br />
# Instanciate a Store with four records<br />
store = data.store.Store([<br />
    {"name": "John Doe", "email": "john@doe.com"},<br />
    {"name": "Jim Doe", "email": "jim@doe.com"},<br />
    {"name": "Robert Doe", "email": "robert@doe.com"},<br />
    {"name": "Melissa Doe", "email": "melissa@doe.com"}<br />
])<br />
<br />
# Find based on value<br />
<br />
results = store.find({"name": "John Doe"})  # One record<br />
<br />
# Find based on regex<br />
import re<br />
regex = re.compile(r"j.*?@\w+\.com")<br />
results = store.find({"email": regex}) # Two records<br />
<br />
# limiting to one result<br />
results = store.find_one({"email": regex}) # One Record<br />
<br />
# find based on callable<br />
results = store.find({"email": lambda x: x.startswith("r")})  # One Record<br />
<br />
# Add a record<br />
store.add_record({"name": "ilovetux", "email": "me@ilovetux.com"})<br />
<br />
# Delete a record based on value<br />
store.del_record({"name": "Melissa Doe"})  # Deletes one record<br />
<br />
# Delete multiple records based on callable<br />
store.del_records({"name": lambda x: x.startswith("J")})<br />
<br />
# Persist the store<br />
store.persist("/var/data/users.db")<br />
<br />
# Load a persisted store<br />
store2 = data.store.load("/var/data/users.db")<br />
<br />
# Find a set of records and sanitize a field on them<br />
store2.find(<br />
    {"email": lambda x: x.startswith("m")},<br />
    sanitize_list=["email"])<br />
```<br />
<br />
The REST API<br />
<br />
A REST API is included in the package for convenience. The<br />
API is a WSGI application written in bottle, and supports<br />
full CRUD operations on records and collections (or Stores<br />
as I have been calling them).<br />
<br />
#### Using the REST API<br />
<br />
The REST API provides the following endpoints:<br />
<br />
##### Collection endpoints<br />
<br />
GET    -> /collections              = list all collections available<br />
<br />
POST   -> /collections/<collection> = Creates a new collection<br />
<br />
DELETE -> /collections/<collection> = Deletes a collection<br />
<br />
##### Record endpoints<br />
<br />
GET    -> /collections/<collection>/records = get a list of records<br />
       matching the keys and values passed through the query string.<br />
<br />
POST   -> /collections/<collection>/records = adds a record to collection<br />
<br />
DELETE -> /collections/<collection>/records = deletes a record<br />
<br />
PUT    -> /collections/<collection>/records/_id = Update a record<br />
<br />
#### Deploying the REST API<br />
Deployment is relatively easy, and could consist of the<br />
following:<br />
<br />
```python<br />
from data.store.api import api<br />
<br />
api.run(server="cherrypy")<br />
```<br />
<br />
or to use a different server (in this case twisted):<br />
<br />
```python<br />
from data.store.api import api<br />
<br />
api.run(server="twisted")<br />
```<br />
<br />
then save either of these files as datastore_api.py<br />
and run<br />
<br />
    $ python datastore_api.py<br />
<br />
and by default the server will listen on port 8080.<br />
<br />
Now, This is one way to deploy it, there are others,<br />
here are some links pointing to some documentation<br />
about deploying WSGI applications (and bottle WSGI<br />
applications in particular):<br />
<br />
To see a list of available servers, check out:<br />
http://bottlepy.org/docs/dev/deployment.html#switching-the-server-backend<br />
<br />
or to see how to deploy it behind Apache httpd check out:<br />
http://bottlepy.org/docs/dev/deployment.html#apache-mod-wsgi<br />
<br />
or on google app engine:<br />
http://bottlepy.org/docs/dev/deployment.html#google-appengine<br />
<br />
or for some info on deploying behind a load balancer:<br />
http://bottlepy.org/docs/dev/deployment.html#load-balancer-manual-setup<br />
<br />
Help and Contributions<br />
<br />
Please feel free to open an issue here on GitHub.<br />
<br />
Contributions in the form of source code are expected to adhere as closely as<br />
possible to PEP 8 also any feature or bug fix needs a unit test. I will <br />
probably cherry pick from the pull requests, so please don't be offended<br />
if I only implement a subset of your change.<br />
''',
      author='iLoveTux',
      author_email='me@ilovetux.com',
      maintainer="ilovetux",
      url='https://github.com/iLoveTux/data_store',
      packages=['data', 'data.store'],
      license="GPL v2",
      install_requires=["bottle == 0.12.8"]
     )
