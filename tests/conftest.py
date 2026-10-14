from typing import Generator
import pytest
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
from mop import create_app


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    test_app = create_app({
        'TESTING': True,
        'CACHE_TYPE': 'NullCache'})
    with test_app.app_context():
        yield test_app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()  # pragma: no cover
