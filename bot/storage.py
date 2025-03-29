import tarantool
from app.models import Poll, CreatePoll, Vote
import uuid

conn = tarantool.Connection("tarantool", 3301)

def create_poll(data: CreatePollR) -> Poll:
    poll_id = str(uuid.uuid4())
    variants = {v: {"title": v, "votes": 0} for v in data.variants}

    poll = {'id': poll_id, 'text': data.text, 'variants': variants, 'author': data.author, 'is_open': True}

    conn.insert("polls", [poll_id, poll])
    return Poll(**poll)

def get_poll(poll_id: str) -> Poll:
    result = conn.select("polls", [poll_id])
    if not result:
        raise Exception("Poll does not found")
    return Poll(**result[0][1])

def vote(poll_id: str, vote: Vote):
    poll = get_poll(poll_id)

    if not poll.is_open:
        raise Exception("Poll is not open")

    if vote.variant not in poll.variants:
        raise Exception("Invalid variant")

    poll.variants[vote.variant].votes += 1
    conn.replace("polls", [poll_id, poll.dict()])

def close_poll(poll_id: str, user: str):
    poll = get_poll(poll_id)
    if poll.creator != user:
        raise Exception("You don't have need rights to do this")
    poll.is_open = False
    conn.replace("polls", [poll_id, poll.dict()])

def delete_poll(poll_id: str):
    conn.delete("polls", [poll_id])