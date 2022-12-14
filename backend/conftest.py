import random
import datetime
import string
import pytest

import typing as Typing
from faker import Faker

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database

from fastapi.testclient import TestClient

from app.main import app

from app.db.enums import Status


from app.db import models
from app.db.session import Base, get_db
from app.core import config, security

fake = Faker()


def get_test_db_url() -> str:
    return f"{config.SQLALCHEMY_DATABASE_URI}_test"


@pytest.fixture(autouse=True)
def test_db():
    """
    Modify the db session to automatically roll back after each test.
    This is to avoid tests affecting the database state of other tests.
    """
    # Connect to the test database
    engine = create_engine(
        get_test_db_url(),
    )

    connection = engine.connect()
    trans = connection.begin()

    # Run a parent transaction that can roll back all changes
    test_session_maker = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    test_session = test_session_maker()
    test_session.begin_nested()

    @event.listens_for(test_session, "after_transaction_end")
    def restart_savepoint(s, transaction):
        if transaction.nested and not transaction._parent.nested:
            s.expire_all()
            s.begin_nested()

    yield test_session

    # Roll back the parent transaction after the test is complete
    test_session.close()
    trans.rollback()
    connection.close()


@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    """
    Create a test database and use it for the whole test session.
    """

    test_db_url = get_test_db_url()

    # Create the test database
    assert not database_exists(
        test_db_url
    ), "Test database already exists. Aborting tests."
    create_database(test_db_url)
    test_engine = create_engine(test_db_url)
    Base.metadata.create_all(test_engine)

    # Run the tests
    yield

    # Drop the test database
    drop_database(test_db_url)


@pytest.fixture(autouse=True)
def client(test_db):
    """
    Get a TestClient instance that reads/write to the test database.
    """

    def get_test_db():
        yield test_db

    app.dependency_overrides[get_db] = get_test_db

    yield TestClient(app)


# Service
@pytest.fixture(autouse=True)
def test_service(test_db) -> models.Service:
    """
    Make a test service in the database
    """
    service = models.Service(
        name=fake.name(),
        description=fake.name(),
        status=Status.ACTIVE.value
    )
    test_db.add(service)
    test_db.commit()
    return service


# Country
@pytest.fixture(autouse=True)
def test_country(test_db) -> models.Service:
    """
    Make a test service in the database
    """
    country_data = models.Country(
        name=fake.name(),
        description=fake.name(),
        status=Status.ACTIVE.value
    )
    test_db.add(country_data)
    test_db.commit()
    return country_data