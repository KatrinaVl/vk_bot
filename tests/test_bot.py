import json
import logging
import os
import socket
import time
import urllib
import uuid

import pytest
import requests

LOGGER = logging.getLogger(__name__)


def wait_for_socket(host, port):
    retries = 10
    exception = None
    while retries > 0:
        try:
            socket.socket().connect((host, port))
            return
        except ConnectionRefusedError as e:
            exception = e
            print(f'Got ConnectionError for url {host}:{port}: {e} , retrying')
            retries -= 1
            time.sleep(2)
    raise exception


@pytest.fixture
def bot_addr():
    addr = os.environ.get('BOT_SERVER_URL', 'http://0.0.0.0:8090')
    host = urllib.parse.urlparse(addr).hostname
    port = urllib.parse.urlparse(addr).port
    wait_for_socket(host, port)
    yield addr


def make_requests(method, addr, handle, params=None, data=None, cookies=None):
    if data is not None:
        data = json.dumps(data)
    req = requests.Request(
        method,
        addr +
        handle,
        params=params,
        data=data,
        cookies=cookies)
    prepared = req.prepare()
    LOGGER.info(f'>>> {prepared.method} {prepared.url}')
    if len(req.data) > 0:
        LOGGER.info(f'>>> {req.data}')
    if req.cookies is not None:
        LOGGER.info(f'>>> {req.cookies}')
    s = requests.Session()
    resp = s.send(prepared)
    LOGGER.info(f'<<< {resp.status_code}')
    if len(resp.content) > 0:
        LOGGER.info(f'<<< {resp.content}')
    if len(resp.cookies) > 0:
        LOGGER.info(f'<<< {resp.cookies}')
    return resp



class Tests:

    @staticmethod
    def test_create(bot_addr):
        r = make_requests(
            'POST',
            bot_addr,
            '/create',
            data={
                "text": "Where do you study?",
                "variants" : ["hse", "mgu"],
                "author": "user_1"})
        assert r.status_code == 201

    @staticmethod
    def test_vote(bot_addr):
        r_poll = make_requests(
            'POST',
            bot_addr,
            '/create',
            data={
                "text": "Where do you study?",
                "variants" : ["hse", "mgu"],
                "author": "user_1"})
        assert r_poll.status_code == 201
        poll_id = json.loads(r_poll.content)['ID']

        r = make_requests(
            'POST',
            bot_addr,
            '/vote',
            data={
                "poll_id": poll_id,
                "variant" : "hse",
                "user" : "user_2"})
        assert r.status_code == 200

    @staticmethod
    def test_wrong_variant(bot_addr):
        r_poll = make_requests(
            'POST',
            bot_addr,
            '/create',
            data={
                "text": "Where do you study?",
                "variants" : ["hse", "mgu"],
                "author": "user_1"})
        assert r_poll.status_code == 201
        poll_id = json.loads(r_poll.content)['ID']

        r = make_requests(
            'POST',
            bot_addr,
            '/vote',
            data={
                "poll_id": poll_id,
                "variant" : "spbgu",
                "user" : "user_2"})
        assert r.status_code == 400


    @staticmethod
    def test_results(bot_addr):
        r_poll = make_requests(
            'POST',
            bot_addr,
            '/create',
            data={
                "text": "Where do you study?",
                "variants" : ["hse", "mgu"],
                "author": "user_1"})
        assert r_poll.status_code == 201
        poll_id = json.loads(r_poll.content)['ID']

        r = make_requests(
            'GET',
            bot_addr,
            '/get_result',
            data={
                "poll_id": poll_id})
        variants = json.loads(r.content)['variants']
        assert variants['hse'] == 0
        assert variants['mgu'] == 0

        r_vote = make_requests(
            'POST',
            bot_addr,
            '/vote',
            data={
                "poll_id": poll_id,
                "variant" : "hse",
                "user" : "user_2"})

        assert r_vote.status_code == 200

        r = make_requests(
            'GET',
            bot_addr,
            '/get_result',
            data={
                "poll_id": poll_id})

        assert r.status_code == 200

        variants = json.loads(r.content)['variants']
        assert variants['hse'] == 1
        assert variants['mgu'] == 0

    
    @staticmethod
    def test_wrong_poll(bot_addr):
        r_poll = make_requests(
            'POST',
            bot_addr,
            '/create',
            data={
                "text": "Where do you study?",
                "variants" : ["hse", "mgu"],
                "author": "user_1"})
        assert r_poll.status_code == 201
        poll_id = json.loads(r_poll.content)['ID']


        r_vote = make_requests(
            'POST',
            bot_addr,
            '/vote',
            data={
                "poll_id": poll_id,
                "variant" : "hse",
                "user" : "user_2"})
        assert r_vote.status_code == 200

        r = make_requests(
            'GET',
            bot_addr,
            '/get_result',
            data={
                "poll_id": '78975'})

        assert r.status_code == 404


    @staticmethod
    def test_close(bot_addr):
        r_poll = make_requests(
            'POST',
            bot_addr,
            '/create',
            data={
                "text": "Where do you study?",
                "variants" : ["hse", "mgu"],
                "author": "user_1"})
        assert r_poll.status_code == 201
        poll_id = json.loads(r_poll.content)['ID']

        r_vote = make_requests(
            'POST',
            bot_addr,
            '/vote',
            data={
                "poll_id": poll_id,
                "variant" : "hse",
                "user" : "user_2"})

        assert r_vote.status_code == 200

        r = make_requests(
            'POST',
            bot_addr,
            '/close',
            data={
                "poll_id": poll_id, 
                "user" : "user_1"})
        assert r.status_code == 200

        r_result = make_requests(
            'GET',
            bot_addr,
            '/get_result',
            data={
                "poll_id": poll_id})

        assert r_result.status_code == 200

        opened = json.loads(r_result.content)['is_open']
        assert opened == False


    @staticmethod
    def test_vote_with_close_poll(bot_addr):
        r_poll = make_requests(
            'POST',
            bot_addr,
            '/create',
            data={
                "text": "Where do you study?",
                "variants" : ["hse", "mgu"],
                "author": "user_1"})
        poll_id = json.loads(r_poll.content)['ID']
        assert r_poll.status_code == 201

        r_close = make_requests(
            'POST',
            bot_addr,
            '/close',
            data={
                "poll_id": poll_id, 
                "user" : "user_1"})
        assert r_close.status_code == 200

        r = make_requests(
            'POST',
            bot_addr,
            '/vote',
            data={
                "poll_id": poll_id,
                "variant" : "hse",
                "user" : "user_2"})
        assert r.status_code == 400


    @staticmethod
    def test_close_with_wrong_rights(bot_addr):
        r_poll = make_requests(
            'POST',
            bot_addr,
            '/create',
            data={
                "text": "Where do you study?",
                "variants" : ["hse", "mgu"],
                "author": "user_1"})
        assert r_poll.status_code == 201
        poll_id = json.loads(r_poll.content)['ID']

        r = make_requests(
            'POST',
            bot_addr,
            '/close',
            data={
                "poll_id": poll_id, 
                "user" : "user_2"})
        assert r.status_code == 400

        r_result = make_requests(
            'GET',
            bot_addr,
            '/get_result',
            data={
                "poll_id": poll_id})

        assert r_result.status_code == 200

        opened = json.loads(r_result.content)['is_open']
        assert opened == True


    @staticmethod
    def test_delete(bot_addr):
        r_poll = make_requests(
            'POST',
            bot_addr,
            '/create',
            data={
                "text": "Where do you study?",
                "variants" : ["hse", "mgu"],
                "author": "user_1"})

        assert r_poll.status_code == 201
        poll_id = json.loads(r_poll.content)['ID']

        r = make_requests(
            'DELETE',
            bot_addr,
            '/delete',
            data={
                "poll_id": poll_id,
                "user" : "user_1"})

        assert r.status_code == 200

        r_result = make_requests(
            'GET',
            bot_addr,
            '/get_result',
            data={
                "poll_id": poll_id})

        assert r_result.status_code == 404

    @staticmethod
    def test_delete_wrong_user(bot_addr):
        r_poll = make_requests(
            'POST',
            bot_addr,
            '/create',
            data={
                "text": "Where do you study?",
                "variants" : ["hse", "mgu"],
                "author": "user_1"})

        assert r_poll.status_code == 201
        poll_id = json.loads(r_poll.content)['ID']

        r = make_requests(
            'DELETE',
            bot_addr,
            '/delete',
            data={
                "poll_id": poll_id,
                "user" : "user_2"})

        assert r.status_code == 400

        r_result = make_requests(
            'GET',
            bot_addr,
            '/get_result',
            data={
                "poll_id": poll_id})

        assert r_result.status_code == 200
        

