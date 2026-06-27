import json
import os


class InputStoreError(Exception):
  """Raised when the input store cannot be read, written, or parsed."""


class InputStore:

  def __init__(self, input_file):
    self.input_file = input_file
    self.data = None

    # create directory if it doesn't exist (skip for bare filenames like 'input.json')
    directory = os.path.dirname(input_file)
    if directory:
      try:
        os.makedirs(directory, exist_ok=True)
      except OSError as e:
        raise InputStoreError(
            f"Cannot create input-store directory '{directory}': {e}"
        ) from e

    # create file if it doesn't exist
    if not os.path.exists(input_file):
      try:
        with open(input_file, 'w') as f:
          json.dump({}, f)
      except OSError as e:
        raise InputStoreError(
            f"Cannot create input-store file '{input_file}': {e}"
        ) from e

  def load(self):
    try:
      with open(self.input_file, 'r') as f:
        self.data = json.load(f)
    except OSError as e:
      raise InputStoreError(
          f"Cannot read input-store file '{self.input_file}': {e}"
      ) from e
    except json.JSONDecodeError as e:
      raise InputStoreError(
          f"Input-store file '{self.input_file}' contains invalid JSON: {e}"
      ) from e

  def get_data(self):
    return self.data

  def get_value(self, key):
    return self.data[key]

  def set_value(self, key, value):
    self.data[key] = value

  def save(self):
    try:
      with open(self.input_file, 'w') as f:
        json.dump(self.data, f, indent=2)
    except OSError as e:
      raise InputStoreError(
          f"Cannot write input-store file '{self.input_file}': {e}"
      ) from e
