import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from logs.functions import log_api_post_edition

class DummySession:
    def __init__(self):
        self.add_called = False
        self.commit_called = False
    def add(self, obj):
        self.add_called = True
    def commit(self):
        self.commit_called = True

class DummyDB:
    def __init__(self):
        self.session = DummySession()

dummy_db = DummyDB()

def test_log_api_post_edition(monkeypatch):
    class DummyKey:
        edit_post = 0
    class DummyUser:
        name = 'tester'
        email = 'tester@example.com'
    class DummyPost:
        id = 1
        title = 'old title'
        subtitle = 'old subtitle'
        body = 'body'
        img_url = ''

    monkeypatch.setattr('logs.functions.load_api_key', lambda user: DummyKey())
    monkeypatch.setattr('logs.functions.db', dummy_db)

    log_api_post_edition(DummyPost(), {'title': 'new title'}, DummyUser())

    assert dummy_db.session.add_called
    assert dummy_db.session.commit_called
