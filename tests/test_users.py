import schemas
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from main import app
from database import get_db,Base
from config import settings
import jwt
from config import settings
from oauth2 import create_access_token
import models

DATABASE_URL =f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'


# Create database engine
engine = create_engine(DATABASE_URL)

TesingSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)


#client = TestClient(app)
@pytest.fixture
def session():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    db = TesingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(session):
    def override_get_db():
        #db = TesingSessionLocal()
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

@pytest.fixture
def test_user(client):
    user = {"email": "mz@gmail.com","password": "password"}
    res = client.post('/users/',json = user)
    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user["password"]
    return new_user
    

def test_root(client):
    res = client.get("/")
    print(res.json().get('message'))
    assert res.json().get('message') == 'Welcome to my Posts API'
    assert res.status_code == 200

def test_create_user(client):
    res = client.post('/users/', json={"email":"hell@gmail.com", "password":"password123"})
    new_user = schemas.UserOut(**res.json())
    assert new_user.email == "hell@gmail.com"
    assert res.status_code == 201

def test_get_user(test_user,client): 
    final_res = client.get('/users/1')
    #print(final_res)
    assert final_res.json().get('id') == 1
    assert final_res.status_code == 200

def test_login(test_user,client):
    res = client.post('/login', data={"username":test_user["email"], "password":test_user["password"]})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token,settings.secret_key,algorithms=[settings.algorithm])
    id = payload.get('user_id')
    assert id == test_user['id']
    print(login_res)
    assert login_res.token_type == "Bearer"
    assert res.status_code == 200

@pytest.mark.parametrize("email, password, status_code",[
    ('wfd@gmail.com','password',403),
    ('sanjeev@gmail.com','password',403),
    ('mvd@gmail.com','password',403),
    ('wfd@gmail.com','password',403),
    (None,'password',403),
    ('wfd@gmail.com',None,403)])

def test_incorrect_login(test_user, client,email,password,status_code):
    res = client.post('/login', data={"username":email, "password":password})
    assert res.status_code == status_code

@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})

@pytest.fixture
def authorised_client(client,token):
    client.headers = {
        **client.headers,
        "Authorization" : f"Bearer {token}"
    }
    return client

def test_get_all_posts(authorised_client):
    res = authorised_client.get('/posts/')
    assert res.status_code == 200

@pytest.fixture
def test_posts(test_user,session):
    posts_data = [{
  "title": "alcist",
  "content": "scice",
  "owner_id": test_user['id']
},{"title": "da",
  "content": "as",
  "owner_id": test_user['id']},{"title": "alcdfist",
  "content": "scidfdce",
  "owner_id": test_user['id']}]
    
    def create_user_model(post):
        return models.Post(**post)
    post_map = map(create_user_model, posts_data)
    posts = list(post_map)
    session.add_all(posts)
    session.commit()
    posts = session.query(models.Post).all()
    return posts

def test_all_posts(authorised_client, test_posts):
    res = authorised_client.get('/posts/')
    print(res.json())
    assert res.status_code == 200