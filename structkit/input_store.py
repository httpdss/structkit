import json
import os


class InputStore:

  def __init__(self, input_file):
    self.input_file = input_file
    self.data = None

    # create directory if it doesn't exist
    directory = os.path.dirname(input_file)
    if not os.path.exists(directory):
      os.makedirs(directory)

    # create file if it doesn't exist
    if not os.path.exists(input_file):
      with open(input_file, 'w') as f:
        json.dump({}, f)

  def load(self):
    with open(self.input_file, 'r') as f:
      self.data = json.load(f)

  def get_data(self):
    return self.data

  def get_value(self, key):
    return self.data[key]

  def set_value(self, key, value):
    self.data[key] = value

  def save(self):
    with open(self.input_file, 'w') as f:
      json.dump(self.data, f, indent=2)
