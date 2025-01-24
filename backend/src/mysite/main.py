import os
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://192.168.77.142",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


MONGODB_URI = os.environ["MONGODB_URI"]

client = AsyncIOMotorClient(MONGODB_URI, uuidRepresentation="standard")

db = client.todolist


class TodoItem(BaseModel):
    id: UUID = Field(default_factory=uuid4, alias="todo_id")
    content: str


class TodoItemCreate(BaseModel):
    content: str


@app.post("/todos", response_model=TodoItem)
async def create_todo(item: TodoItemCreate):
    new_todo = TodoItem(content=item.content)
    await db.todos.insert_one(new_todo.model_dump(by_alias=True))
    return new_todo


@app.get("/todos", response_model=list[TodoItem])
async def read_todos():
    return await db.todos.find().to_list(length=None)


@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: UUID):
    delete_result = await db.todos.delete_one({"todo_id": todo_id})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}
