from flask import Flask, request, jsonify
from db import Database
from dataclasses import dataclass

app = Flask ()

@app.route ("/")
def main () : 
    return "Hello World!"

if __name__ == "__main__" :
    app.run (port = 6000, debug = True)