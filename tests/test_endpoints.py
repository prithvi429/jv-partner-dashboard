from fastapi.testclient import TestClient
import backend
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models
from database import get_db

# Create a TestClient using an in-memory SQLite DB
engine = create_engine('sqlite:///:memory:')
models.Base.metadata.create_all(bind=engine)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

backend.app.dependency_overrides[get_db] = override_get_db
client = TestClient(backend.app)


def test_root():
    res = client.get('/')
    assert res.status_code == 200


def test_create_and_list_deal():
    payload = {
        "name": "Unit Test Deal",
        "company_name": "UT Co",
        "product_name": "UT Product",
        "value": 500.0,
    }
    r = client.post('/deals/', json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data['name'] == payload['name']

    r2 = client.get('/deals/')
    assert r2.status_code == 200
    arr = r2.json()
    assert any(d['name'] == payload['name'] for d in arr)
