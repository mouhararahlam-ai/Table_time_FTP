import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

import models
import crud
import schemas

# Create test database (in memory)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

models.Base.metadata.create_all(bind=engine)

@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_create_task(db):
    task = schemas.TaskCreate(
        title="Test Task",
        description="Test Description",
        deadline=datetime.now(),
        status="pending"
    )
    db_task = crud.create_task(db, task)
    assert db_task.id is not None
    assert db_task.title == "Test Task"


def test_get_task(db):
    task = schemas.TaskCreate(
        title="Task",
        description="Desc",
        deadline=datetime.now(),
        status="pending"
    )
    created = crud.create_task(db, task)
    fetched = crud.get_task(db, created.id)
    assert fetched.id == created.id


def test_update_task(db):
    task = schemas.TaskCreate(
        title="Old",
        description="Desc",
        deadline=datetime.now(),
        status="pending"
    )
    created = crud.create_task(db, task)

    update = schemas.TaskUpdate(title="New")
    updated = crud.update_task(db, created.id, update)

    assert updated.title == "New"

def test_delete_task(db):
    task = schemas.TaskCreate(
        title="Delete",
        description="Desc",
        deadline=datetime.now(),
        status="pending"
    )
    created = crud.create_task(db, task)

    result = crud.delete_task(db, created.id)
    assert result is True

    assert crud.get_task(db, created.id) is None