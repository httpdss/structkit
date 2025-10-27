import pytest
import json
import os
from structkit.input_store import InputStore

@pytest.fixture
def input_store(tmp_path):
    input_file = tmp_path / "input.json"
    return InputStore(input_file)

def test_load(input_store):
    data = {"key": "value"}
    with open(input_store.input_file, 'w') as f:
        json.dump(data, f)
    input_store.load()
    assert input_store.get_data() == data

def test_get_value(input_store):
    data = {"key": "value"}
    with open(input_store.input_file, 'w') as f:
        json.dump(data, f)
    input_store.load()
    assert input_store.get_value("key") == "value"

def test_set_value(input_store):
    input_store.load()
    input_store.set_value("key", "value")
    assert input_store.get_value("key") == "value"

def test_save(input_store):
    input_store.load()
    input_store.set_value("key", "value")
    input_store.save()
    with open(input_store.input_file, 'r') as f:
        data = json.load(f)
    assert data == {"key": "value"}
