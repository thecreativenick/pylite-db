import sqlite3

import pytest

from pylite.header import DatabaseHeader, HeaderError, read_header


def make_db(path, page_size=4096):
    con = sqlite3.connect(path)
    con.execute(f"PRAGMA page_size={page_size}")
    con.execute("CREATE TABLE t(a INTEGER PRIMARY KEY, b TEXT)")
    con.executemany("INSERT INTO t(b) VALUES (?)", [(f"row {i}",) for i in range(200)])
    con.execute("PRAGMA user_version=7")
    con.commit()
    con.close()


@pytest.mark.parametrize("page_size", [512, 1024, 4096, 65536])
def test_reads_header_written_by_sqlite(tmp_path, page_size):
    path = tmp_path / "x.db"
    make_db(path, page_size)
    h = read_header(path)
    assert h.page_size == page_size
    assert h.user_version == 7
    assert h.text_encoding == 1
    assert h.database_size_pages * page_size == path.stat().st_size


def test_round_trip_is_byte_identical(tmp_path):
    path = tmp_path / "x.db"
    make_db(path)
    raw = path.read_bytes()[:100]
    assert DatabaseHeader.parse(raw).to_bytes() == raw


def test_rejects_bad_magic():
    with pytest.raises(HeaderError):
        DatabaseHeader.parse(b"not a database".ljust(100, b"\0"))


def test_rejects_bad_page_size():
    with pytest.raises(HeaderError):
        DatabaseHeader(page_size_raw=1000).to_bytes()
