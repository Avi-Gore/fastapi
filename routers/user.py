from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
import models, utils
from database import get_db
from schemas import UserCreate,UserOut

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.post('/', status_code=status.HTTP_201_CREATED,response_model = UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED, detail = "Email already exist in database")
    #hash the password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.get('/{id}',status_code=status.HTTP_200_OK,response_model=UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with {id} not found")
    
    return user