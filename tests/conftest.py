"""Shared fixtures: a fake transport under ``requests.Session.request``."""

import json as _json

import pytest
import requests


def make_response(status=200, payload=None, text=None):
    """Build a real ``requests.Response`` carrying a JSON payload."""
    resp = requests.Response()
    resp.status_code = status
    if text is None:
        text = "" if payload is None else _json.dumps(payload)
    resp._content = text.encode("utf-8")
    resp.encoding = "utf-8"
    return resp


class FakeTransport:
    def __init__(self):
        self.calls = []
        self.queue = []
        self.error = None

    def reply(self, status=200, payload=None, text=None):
        self.queue.append(make_response(status, payload, text))

    @property
    def last(self):
        return self.calls[-1]

    def request(self, method, url, **kwargs):
        self.calls.append({"method": method, "url": url, **kwargs})
        if self.error is not None:
            raise self.error
        return self.queue.pop(0) if self.queue else make_response(200, [])


@pytest.fixture
def http(monkeypatch):
    fake = FakeTransport()

    def request(session, method, url, **kwargs):
        return fake.request(method, url, **kwargs)

    monkeypatch.setattr(requests.Session, "request", request)
    return fake
