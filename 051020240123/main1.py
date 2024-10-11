from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
import re

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Модель пользователя
class User(BaseModel):
    id: int
    username: str
    age: int

users: List[User] = []

# Модель задачи
class Task(BaseModel):
    id: int
    title: str
    content: str
    priority: int
    user_id: int
    completed: bool
    slug: str

tasks: List[Task] = []

# Функция для генерации slug
def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'\s+', '-', text)  # Замена пробелов на дефисы
    text = re.sub(r'[^a-z0-9-]', '', text)  # Удаление недопустимых символов
    return text

# Endpoints for user management
@app.get("/", response_class=HTMLResponse)
async def get_users_list(request: Request):
    return templates.TemplateResponse("users.html", {"request": request, "users": users})

@app.get("/users/{user_id}", response_class=HTMLResponse)
async def get_user(request: Request, user_id: int = Path(..., description="Enter the user ID")):
    user = next((user for user in users if user.id == user_id), None)
    if user is None:
        raise HTTPException(status_code=404, detail="User was not found")
    return templates.TemplateResponse("users.html", {"request": request, "user": user})

@app.post("/user/{username}/{age}", response_model=User)
async def create_user(
    username: str = Path(..., min_length=5, max_length=20, description="Enter username"),
    age: int = Path(..., ge=18, le=120, description="Enter age")
):
    user_id = users[-1].id + 1 if users else 1
    new_user = User(id=user_id, username=username, age=age)
    users.append(new_user)
    return new_user

@app.put("/user/{user_id}/{username}/{age}", response_model=User)
async def update_user(
    user_id: int = Path(..., description="Enter the user ID"),
    username: str = Path(..., min_length=5, max_length=20, description="Enter username"),
    age: int = Path(..., ge=18, le=120, description="Enter age")
):
    for user in users:
        if user.id == user_id:
            user.username = username
            user.age = age
            return user
    raise HTTPException(status_code=404, detail="User was not found")

@app.delete("/user/{user_id}", response_model=User)
async def delete_user(user_id: int = Path(..., description="Enter the user ID to delete")):
    global tasks
    user_to_delete = next((user for user in users if user.id == user_id), None)
    if user_to_delete:
        # Remove associated tasks
        tasks[:] = [task for task in tasks if task.user_id != user_id]
        users.remove(user_to_delete)
        return user_to_delete
    raise HTTPException(status_code=404, detail="User was not found")

# Endpoints for task management
@app.post("/task/", response_model=Task)
async def create_task(title: str, content: str, priority: int, user_id: int):
    task_id = tasks[-1].id + 1 if tasks else 1
    slug = slugify(title)  # Генерация slug
    new_task = Task(id=task_id, title=title, content=content, priority=priority, user_id=user_id, completed=False, slug=slug)
    tasks.append(new_task)
    return new_task

@app.get("/tasks", response_class=HTMLResponse)
async def get_tasks(request: Request):
    return templates.TemplateResponse("tasks.html", {"request": request, "tasks": tasks})

@app.get("/api/tasks", response_model=List[Task])
async def get_all_tasks():
    return tasks

@app.put("/task/{task_id}", response_model=Task)
async def update_task(task_id: int, title: str, content: str, priority: int, user_id: int, completed: bool):
    for task in tasks:
        if task.id == task_id:
            task.title = title
            task.content = content
            task.priority = priority
            task.user_id = user_id
            task.completed = completed
            return task
    raise HTTPException(status_code=404, detail="Task was not found")

@app.delete("/task/{task_id}", response_model=Task)
async def delete_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)
            return task
    raise HTTPException(status_code=404, detail="Task was not found")

# Sample data creation for demonstration
# @app.on_event("startup")
# async def startup_event():
#     # Create sample users
#     users.append(User(id=1, username="User1", age=25))
#     users.append(User(id=2, username="User2", age=30))
#     users.append(User(id=3, username="User3", age=35))
#
#     # Create sample tasks
#     tasks.append(Task(id=1, title="FirstTask", content="Content1", priority=0, user_id=1, completed=False, slug=slugify("FirstTask")))
#     tasks.append(Task(id=2, title="SecondTask", content="Content2", priority=2, user_id=1, completed=False, slug=slugify("SecondTask")))
#     tasks.append(Task(id=3, title="ThirdTask", content="Content3", priority=4, user_id=3, completed=False, slug=slugify("ThirdTask")))
#     tasks.append(Task(id=4, title="FourthTask", content="Content4", priority=6, user_id=3, completed=False, slug=slugify("FourthTask")))