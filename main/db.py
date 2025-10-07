from sqlite3 import connect, Row, Cursor
from typing import Optional, Union, Any, Generator
from contextlib import contextmanager

class Database :
    def __init__ (self) :
        self.filename = "notes.db"
        with self.editor () as cur :
            cur.execute ("""
                        CREATE TABLE IF NOT EXISTS notes (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         title TEXT UNIQUE NOT NULL,
                         content TEXT DEFAULT '',
                         pinned INTEGER DEFAULT 0,
                         trashed INTEGER DEFAULT 0,
                         created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                         modified_at TEXT DEFAULT CURRENT_TIMESTAMP
                         )
                        """)
            
    def add_note (self, title, content, pinned, trashed, created_at, modified_at) -> int :
        with self.editor () as cur :
            cur.execute ("""INSERT INTO notes title, content, pinned, trashed, created_at, modified_at
                         VALUES (?, ?, ?, ?, ?, ?)""", (title, content, pinned, trashed, created_at, modified_at))
            return cur.lastrowid

    @contextmanager
    def editor (self) -> Generator [Cursor, Any, Any] :
        conn = connect (self.filename)
        cur = conn.cursor ()
        try :
            yield cur
            conn.commit ()
        except Exception : 
            conn.rollback ()
            raise
        finally :
            cur.close ()
            conn.close ()