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
    $ py.test  # optionally run the tests
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

# Find based on regex
import re
regex = re.compile(r"j.*?@\w+\.com")
results = store.find({"email": regex}) # Two records

# limiting to one result
results = store.find_one({"email": regex}) # One Records

# find based on callable
results = store.find({"email": lambda x: x.startswith("r")})  # One Record

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

# Find a set of records and sanitize a field on them
store2.find(
    {"email": lambda x: x.startswith("m")},
    sanitize_list=["email"])
```

## Help and Contributions

Please feel free to open an issue here on GitHub.

Contributions in the form of source code are expected to adhere as closely as
possible to PEP 8 also any feature or bug fix needs a unit test. I will 
probably cherry pick from the pull requests, so please don't be offended
if I only implement a subset of your change.
