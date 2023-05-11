import pytest
from fastapi.testclient import TestClient
from deploy_server.main import app


@pytest.fixture(scope="session", autouse=True)
def test_app():
    client = TestClient(app)
    yield client  # provide the test client to the tests
    # teardown code goes here
