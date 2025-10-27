from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version('struct')
except PackageNotFoundError:
    __version__ = "unknown"
