from sqlite3 import connect, Row, Cursor
from typing import Optional, Union, Any, Generator
from contextlib import contextmanager
from datetime import datetime

"""Aether Notes backend - DB Manager"""

class Database :
    """Handles DB operations."""
    def __init__ (self) :
        """Initializes the DB with proper tables."""
        self.filename = "notes.db"
        with self.editor () as cur :
            cur.execute ("""
                        CREATE TABLE IF NOT EXISTS notes (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         title TEXT UNIQUE NOT NULL,
                         content TEXT DEFAULT '',
                         pinned INTEGER DEFAULT 0,
                         created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                         modified_at TEXT DEFAULT CURRENT_TIMESTAMP
                         )
                        """)
            
    def add_note (self, title, content, pinned, created_at = None, modified_at = None) -> int :
        """
        Takes in parameters to create a new note and returns its id. 
        Note :(API handles Note -> params conversion)"""
        with self.editor () as cur :
            cur.execute ("""INSERT INTO notes (title, content, pinned, created_at, modified_at)
                         VALUES (?, ?, ?, ?, ?)""", (title, content, pinned, created_at, modified_at))
            return cur.lastrowid
        
    def all_notes (self, page, per_page) :
        """Returns all the notes in the DB. Has parameters 'page' and 'per_page' to handle pagination."""
        with self.editor () as cur :
            cur.execute ("SELECT * FROM notes ORDER BY pinned DESC, created_at DESC LIMIT ? OFFSET ?",
                          (per_page, (page - 1) * per_page))
            return cur.fetchall ()
        
    def note_by_id (self, note_id) :
        """Returns a note by its id. It is formatted as a raw Row object."""
        with self.editor () as cur :
            cur.execute ("SELECT * FROM notes WHERE id = ?", (note_id,))
            return cur.fetchone ()
        
    def note_by_keyword (self, keyword, page, per_page) :
        """Takes a keyword and returns note that contain a similar version of it in their content.
        Also has 'page' and 'per_page' for pagination."""
        with self.editor () as cur :
            cur.execute ("SELECT * FROM notes WHERE content LIKE ? ORDER BY pinned DESC, created_at DESC LIMIT ? OFFSET ?",
                         (f"%{keyword}%", per_page, (page - 1) * per_page))
            return cur.fetchall ()
        
    def update_note (self, note_id, title : Optional [str], content : Optional [str], pinned : Optional [int]) :
        """Takes in some optional parameters and updates the note at the given 'note_id' with those parameters."""
        with self.editor () as cur :
            args = []
            if title is not None : args.append ("title = ?")
            if content is not None : args.append ("content = ?")
            if pinned is not None : args.append ("pinned = ?")

            values = [arg for arg in [title, content, pinned] if arg is not None]
            now = datetime.now ().isoformat ()
            cur.execute (f"UPDATE notes SET {', '.join (args)}, modified_at = ? WHERE id = ?", tuple (values) + (now, note_id))

    def toggle_pin (self, note_id, pinned : bool) :
        """Toggles the pin of the note at 'note_id'. 
        'pinned' lets it know whether to pin or unpin (the current state of the note is pinned)"""
        with self.editor () as cur :
            cur.execute ("UPDATE notes SET pinned = ? WHERE id = ?", (1 if pinned else 0, note_id))
 
    @contextmanager
    def editor (self) -> Generator [Cursor, Any, Any] :
        conn = connect (self.filename)
        conn.row_factory = Row
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