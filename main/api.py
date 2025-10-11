from flask import Flask, request, jsonify
from db import Database
from dataclasses import dataclass, asdict
from datetime import datetime
from sqlite3 import Row

@dataclass
class Note :
    """A container that keeps data structured."""
    note_id : int
    title : str
    content : str
    pinned : bool
    created_at : datetime
    modified_at : datetime

class NoteManager :
    @staticmethod
    def to_note (row : Row) :
        """Takes in a sqlite3.Row object and converts it to a Note dataclass"""
        return Note (
            row ["note_id"], row ["title"], row ["content"], bool (row ["pinned"]),
            datetime.fromisoformat (row ["created_at"]), datetime.fromisoformat (row ["modified_at"]))
    
    @staticmethod
    def serialize (note : Note) :
        d = asdict (note)
        d ["created_at"] = note.created_at.isoformat ()
        d ["modified_at"] = note.modified_at.isoformat ()

app = Flask (__name__)
db = Database ()

@app.route ("/", methods = ["GET"])
def all_notes () : 
    """Return all notes in the DB. Needs a json payload of type dict,
      with keys page and per_pge for pagination (default to 1 and 10 respectively)"""
    
    data : dict = request.get_json (force = True)
    notes = db.all_notes (data.get ("page", 1), data.get ("per_page", 10))
    notes = [NoteManager.to_note (note) for note in notes]
    return jsonify ([NoteManager.serialize (note) for note in notes]), 200

if __name__ == "__main__" :
    app.run (port = 6000, debug = True)