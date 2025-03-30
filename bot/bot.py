from flask import Flask, jsonify
from flask import request

import json
import requests

from models import Vote
import database 

app = Flask(__name__)

@app.route("/create", methods=['POST'])
def create():
    data = request.get_json(force=True)
    try:
        poll = database.create_poll(data)
        return jsonify({"ID": poll.id, "variants" : list(poll.variants.keys())}), 201
    except Exception as e:
        return {"message" : str(e)}, 400

@app.route("/vote", methods=['POST'])
def vote():
    data = request.get_json(force=True)
    try:
        database.vote(data['poll_id'], Vote(**data))

        return "Vote accepted", 200
    except Exception as e:
        return {"message" : str(e)}, 400

@app.route("/get_result", methods=['GET'])
def get_result():
    data = request.get_json(force=True)

    try:
        poll = database.get_poll(data['poll_id'])

        return {"author" : poll.author, "text": poll.text, "variants": poll.variants, "is_open": poll.is_open}, 200
    except Exception as e:
        return {"message" : str(e)}, 404

@app.route("/close", methods=['POST'])
def close():
    data = request.get_json(force=True)

    try:
        poll = database.close_poll(data['poll_id'], data["user"])

        return "poll is closed", 200
    except Exception as e:
        return {"message" : str(e)}, 400


@app.route("/delete", methods=['DELETE'])
def delete():
    data = request.get_json(force=True)

    try:
        poll = database.delete_poll(data['poll_id'], data['user'])

        return "poll is deleted", 200
    except Exception as e:
        return {"message" : str(e)}, 400

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='8090')