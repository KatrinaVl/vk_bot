import tarantool
from models import Poll, Vote
import uuid

conn = tarantool.Connection("tarantool", 3301)

def create_poll(data):
    poll_id = str(uuid.uuid4())
    variants = {v : 0 for v in data['variants']}

    poll = {'id': poll_id, 'text': data['text'], 
        'variants': variants, 'author': data['author'], 'is_open': True}

    conn.insert("polls", [poll_id, poll])
    return Poll(**poll)

def vote(poll_id, vote):
    poll = get_poll(poll_id)

    if not poll.is_open:
        raise Exception("poll is not open")

    if vote.variant not in poll.variants:
        raise Exception("wrong variant")

    poll.variants[vote.variant] += 1
    conn.replace("polls", [poll_id, poll.dict()])

def get_poll(poll_id) :
    result = conn.select("polls", [poll_id])
    if not result:
        raise Exception("poll does not found")
    return Poll(**result[0][1])

def close_poll(poll_id, user):
    poll = get_poll(poll_id)
    if poll.author != user:
        raise Exception("you don't have need rights")
    poll.is_open = False
    conn.replace("polls", [poll_id, poll.dict()])

def delete_poll(poll_id, user):
    poll = get_poll(poll_id)
    if poll.author != user:
        raise Exception("you don't have need rights")
    conn.delete("polls", [poll_id])