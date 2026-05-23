from typing import Generator
import pytest
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
from mop import app as flask_app


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    flask_app.config.update({
        'TESTING': True,
    })
    yield flask_app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()
