from fastapi import FastAPI
#from sqlalchemy.orm import Session
import models
#from schemas import PostCreate, PostResponse,UserCreate,UserOut
from database import engine
from routers import post,user,auth,vote
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]

)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get('/')
def home():
    return {"message": "Welcome to my Posts API"}

