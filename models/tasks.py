from pydantic import BaseModel
from typing import Optional
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Category(str, Enum):
    WORK = "work"
    PERSONAL = "personal"
    HEALTH = "health"
    STUDY = "study"
    SHOPPING = "shopping"
    GENERAL = "general"

class Task(BaseModel):
    id: int
    title: str
    description: str
    task_time: str
    priority: Priority
    category: Category
    completed: bool = False
    user_id: int

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "id": 1,
                "title": "Совещание с командой",
                "description": "Обсуждение нового проекта",
                "task_time": "14:00",
                "priority": "high",
                "category": "work",
                "completed": False,
                "user_id": 1
            }]
        }
    }

class TaskCreate(BaseModel):
    title: str
    description: str
    task_time: str
    priority: Priority
    category: Category
