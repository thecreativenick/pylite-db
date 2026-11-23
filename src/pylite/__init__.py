"""pylite: a pure-Python engine for the SQLite file format."""

from .header import DatabaseHeader, HeaderError, read_header

__version__ = "0.0.1"
__all__ = ["DatabaseHeader", "HeaderError", "read_header"]
