from fastapi import Depends,status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from database import get_db
import models,oauth2
from utils import verify

from fastapi.security import OAuth2PasswordRequestForm



router = APIRouter(
    tags=['Authentication']
)

@router.post('/login')
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email id does not exist")
    
    if not verify(user_credentials.password,user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Wrong password provided")
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access Token": access_token, "token_type": "Bearer"}


