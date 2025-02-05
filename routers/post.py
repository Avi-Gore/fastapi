from fastapi import Depends, status, HTTPException,APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
import models
from schemas import PostCreate, PostResponse,UserCreate,UserOut,PostOut
from database import engine,get_db
from oauth2 import get_current_user
from typing import List, Optional

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


@router.get('/', response_model = List[PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(get_current_user), Limit: int = 5, skip: int = 0, search: Optional[str] = ""):
    
    #posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(Limit).offset(skip).all()

    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(Limit).offset(skip).all()
    
    return posts

@router.get('/{id}', response_model = PostOut)
def get_post(id: int, db: Session = Depends(get_db),current_user: int = Depends(get_current_user)):
    post =  db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    #print(current_user.email)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with {id} not found")
    
    return post

@router.post('/',status_code=status.HTTP_201_CREATED, response_model = PostResponse)
def create_posts(post: PostCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    # Convert Pydantic model to ORM model

    new_post = models.Post(owner_id=current_user.id,**post.dict())
    # Add and commit to the database
    db.add(new_post)
    db.commit()
    db.refresh(new_post)  # Get the saved data

    return new_post


@router.put('/{id}',status_code=status.HTTP_202_ACCEPTED, response_model = PostResponse)
def update_post(id: int, post: PostCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id).first()
    
    if post_query == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with {id} not found")
    
    if post_query.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You are not the owner of the post {id} ")

    
    post_query.title = post.title
    post_query.content = post.content
    post_query.published = post.published

    # Commit the transaction to save changes
    db.commit()
    db.refresh(post_query)  # Refresh to get updated data

    return post_query

@router.delete('/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with {id} not found")
    
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You are not the owner of the post {id} ")
    
    post_query.delete(synchronize_session= False)
    db.commit()
    return {"msg": "Deleted successfully"}
