"""The 100-byte SQLite database header (https://www.sqlite.org/fileformat.html#the_database_header)."""

from __future__ import annotations

import struct
from dataclasses import dataclass

MAGIC = b"SQLite format 3\x00"
HEADER_SIZE = 100

# (field name, offset, struct format) for every big-endian integer after the magic string.
_LAYOUT = [
    ("page_size_raw", 16, ">H"),
    ("write_version", 18, ">B"),
    ("read_version", 19, ">B"),
    ("reserved_space", 20, ">B"),
    ("max_payload_fraction", 21, ">B"),
    ("min_payload_fraction", 22, ">B"),
    ("leaf_payload_fraction", 23, ">B"),
    ("file_change_counter", 24, ">I"),
    ("database_size_pages", 28, ">I"),
    ("first_freelist_trunk", 32, ">I"),
    ("freelist_page_count", 36, ">I"),
    ("schema_cookie", 40, ">I"),
    ("schema_format", 44, ">I"),
    ("default_cache_size", 48, ">I"),
    ("largest_root_btree", 52, ">I"),
    ("text_encoding", 56, ">I"),
    ("user_version", 60, ">I"),
    ("incremental_vacuum", 64, ">I"),
    ("application_id", 68, ">I"),
    ("version_valid_for", 92, ">I"),
    ("sqlite_version_number", 96, ">I"),
]


class HeaderError(ValueError):
    """Raised when bytes are not a valid SQLite header."""


@dataclass
class DatabaseHeader:
    page_size_raw: int = 4096
    write_version: int = 1
    read_version: int = 1
    reserved_space: int = 0
    max_payload_fraction: int = 64
    min_payload_fraction: int = 32
    leaf_payload_fraction: int = 32
    file_change_counter: int = 1
    database_size_pages: int = 1
    first_freelist_trunk: int = 0
    freelist_page_count: int = 0
    schema_cookie: int = 0
    schema_format: int = 4
    default_cache_size: int = 0
    largest_root_btree: int = 0
    text_encoding: int = 1  # 1 = UTF-8
    user_version: int = 0
    incremental_vacuum: int = 0
    application_id: int = 0
    version_valid_for: int = 1
    sqlite_version_number: int = 3046000

    @property
    def page_size(self) -> int:
        """Page size in bytes; the stored value 1 means 65536."""
        return 65536 if self.page_size_raw == 1 else self.page_size_raw

    @classmethod
    def parse(cls, data: bytes) -> "DatabaseHeader":
        if len(data) < HEADER_SIZE:
            raise HeaderError(f"header needs {HEADER_SIZE} bytes, got {len(data)}")
        if data[:16] != MAGIC:
            raise HeaderError("missing 'SQLite format 3' magic string")
        values = {name: struct.unpack_from(fmt, data, off)[0] for name, off, fmt in _LAYOUT}
        header = cls(**values)
        header.validate()
        return header

    def validate(self) -> None:
        size = self.page_size
        if size < 512 or size > 65536 or size & (size - 1):
            raise HeaderError(f"page size {size} is not a power of two in 512..65536")
        if (self.max_payload_fraction, self.min_payload_fraction, self.leaf_payload_fraction) != (64, 32, 32):
            raise HeaderError("payload fractions must be 64/32/32")
        if self.text_encoding not in (1, 2, 3):
            raise HeaderError(f"unknown text encoding {self.text_encoding}")

    def to_bytes(self) -> bytes:
        self.validate()
        buf = bytearray(HEADER_SIZE)
        buf[:16] = MAGIC
        for name, off, fmt in _LAYOUT:
            struct.pack_into(fmt, buf, off, getattr(self, name))
        return bytes(buf)


def read_header(path: str) -> DatabaseHeader:
    with open(path, "rb") as fh:
        return DatabaseHeader.parse(fh.read(HEADER_SIZE))


__all__ = ["DatabaseHeader", "HeaderError", "read_header", "MAGIC", "HEADER_SIZE"]
