from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("benefits")
except PackageNotFoundError:
    # package is not installed
    pass


VERSION = __version__
