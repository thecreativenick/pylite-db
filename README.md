# pylite-db

A database engine in pure Python that reads and writes real SQLite files, built from the
[published file-format spec](https://www.sqlite.org/fileformat.html). The stock `sqlite3`
tool should be able to open, query and integrity-check every file it produces.

## Status

Early scaffold. Done so far:

- `pylite.header` parses and writes the 100-byte database header, tested against files made by
  Python's `sqlite3` module.

## Planned milestones

1. Pager: read and write fixed-size pages, track the database size.
2. B-tree pages: table leaf and interior cells, varints, record format, overflow pages.
3. Read path: walk `sqlite_schema`, scan tables, read files made by `sqlite3`.
4. Write path: insert and delete with page splits and merges, freelist.
5. Indexes and a SQL subset: `CREATE TABLE/INDEX`, `INSERT`, `DELETE`, `SELECT ... WHERE`.
6. Local web page that draws a file's B-tree pages.

## Success bar

After 50,000 random operations, `sqlite3`'s `PRAGMA integrity_check` returns `ok`, every row
matches an in-memory model, and pylite reads files that `sqlite3` wrote.

## Development

```bash
pip install -e .[dev]
pytest
```
