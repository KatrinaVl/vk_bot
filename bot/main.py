from flask import Flask, jsonify
from flask import request
from flask import make_response

import json
import requests
import logging

from bot.models import CreatePoll, Vote
import bot.storage as storage


app = Flask(__name__)
LOGGER = logging.getLogger(__name__)

@app.route("/polls", methods=['POST'])
def create():
    d = request.get_json(force=True)

    try:
        poll = storage.create_poll(data)
        return jsonify{
            "message": "Poll created",
            "id": poll.id,
            "options": list(poll.options.keys())
        }, 201

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    bot.run(debug=True, host='0.0.0.0', port='8090')