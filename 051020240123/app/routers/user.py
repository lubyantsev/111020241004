from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import User, Task
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import select, insert, update

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/")
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.execute(select(User)).scalars().all()
    return users


@router.get("/{user_id}")
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User was not found")
    return user


@router.post("/create")
async def create_user(new_user: CreateUser, db: Session = Depends(get_db)):
    db.execute(insert(User).values(new_user.dict(exclude_unset=True)))
    db.commit()
    return {"message": "User created successfully"}


@router.put("/update/{user_id}", response_model=dict)
async def update_user(user_id: int, user: UpdateUser, db: Annotated[Session, Depends(get_db)]):
    existing_user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User was not found")

    db.execute(update(User).where(User.id == user_id).values(user.dict()))
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}


@router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Удаление связанных задач
    db.query(Task).filter(Task.user_id == user_id).delete()
    db.delete(user)
    db.commit()


@router.get("/{user_id}/tasks", response_model=list[Task])
async def tasks_by_user_id(user_id: int, db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.user_id == user_id).all()
    return tasks
