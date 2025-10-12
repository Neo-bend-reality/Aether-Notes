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
        """Takes in a sqlite3.Row object and converts it to a Note dataclass."""
        return Note (
            row ["note_id"], row ["title"], row ["content"], bool (row ["pinned"]),
            datetime.fromisoformat (row ["created_at"]), datetime.fromisoformat (row ["modified_at"]))
    
    @staticmethod
    def serialize (note : Note) :
        """Serializes a note object into JSON format - currently returns a dict. 
        Converts the datetime objects into ISO format."""
        d = asdict (note)
        d ["created_at"] = note.created_at.isoformat ()
        d ["modified_at"] = note.modified_at.isoformat ()
        return d

app = Flask (__name__)
db = Database ()

@app.route ("/", methods = ["GET"])
def all_notes (): 
    """Return all notes in the DB. Gives them as a list with status code 200. 
    Use search queries to pass the parameters. Example requests :-
    http://localhost:6000/?page=1&per_page=10
    http://localhost:6000/?page=2&per_page=5
    """

    page = max (1, int (request.args.get ("page", 1)))
    per_page = max (1, int (request.args.get ("per_page", 10)))
    notes = db.all_notes (page, per_page)
    if notes :
        notes = [NoteManager.to_note (note) for note in notes]
        return jsonify ([NoteManager.serialize (note) for note in notes]), 200
    return jsonify ([]), 200

@app.route ("/search/<int:note_id>", methods = ["GET"])
def note_by_id (note_id : int) :
    """Returns a note by its id. Use the URL to pass the ID.
    It will return 200 for success and 404 if the note isn't found. Example requests :
    http://localhost:6000/search/1
    http://localhost:6000/search/42"""

    note = db.note_by_id (note_id)
    if note : 
        return jsonify (NoteManager.serialize (NoteManager.to_note (note))), 200
    return jsonify ({"message" : "Note not found"}), 404

@app.route ("/search/", methods = ["GET"])
def note_by_keyword () :
    """Returns notes that have the given keyword in their content. Use search queries to pass parameters. Exaple requests :-
    http://localhost:6000/search/?keyword=note
    http://localhost:6000/search/?keyword=todo&page=1&per_page=5"""
    
    keyword = request.args.get ("keyword")
    if not keyword : 
        return jsonify ({"message" : "Keyword required"}), 400
    page = max (1, int (request.args.get ("page", 1)))
    per_page = max (1, int (request.args.get ("per_page", 10)))
    notes = db.note_by_keyword (keyword, page, per_page)

    if notes : 
        notes = [NoteManager.to_note (note) for note in notes]
        return jsonify ([NoteManager.serialize (note) for note in notes]), 200
    return jsonify ([]), 200

if __name__ == "__main__" :
    app.run (port = 6000, debug = True)