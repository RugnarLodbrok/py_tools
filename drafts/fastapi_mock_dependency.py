import pytest
from fastapi import Depends, FastAPI, Header
from fastapi.testclient import TestClient

app = FastAPI()
client = TestClient(app)


def my_headers_dep(h1: str = Header('key1'), h2: str = Header('key2')):
    return h1, h2


@app.get('/test')
async def get_test(my_headers: tuple[str, str] = Depends(my_headers_dep)):
    return {'my_headers': my_headers}


@pytest.fixture()
def fake_dependency():
    def fake():
        return 'a', 'b'

    app.dependency_overrides[my_headers_dep] = fake
    yield
    app.dependency_overrides.pop(my_headers_dep)


def test_default():
    r = client.get('/test')
    assert r.json() == {'my_headers': ['key1', 'key2']}


def test_fake_dependency(fake_dependency):
    r = client.get('/test')
    assert r.json() == {'my_headers': ['a', 'b']}
