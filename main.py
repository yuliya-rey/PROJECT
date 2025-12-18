from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import sqlite3
import hashlib
import secrets
import uvicorn

app = FastAPI(title="Планировщик")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Простое хранилище сессий
sessions = {}

# Дни недели
WEEK_DAYS = {
    'monday': 'Понедельник',
    'tuesday': 'Вторник', 
    'wednesday': 'Среда',
    'thursday': 'Четверг',
    'friday': 'Пятница',
    'saturday': 'Суббота',
    'sunday': 'Воскресенье'
}

# Категории
CATEGORIES = {
    'work': '💼 Работа',
    'study': '📚 Учеба',
    'health': '🏥 Здоровье',
    'general': '📋 Общее'
}

def get_db():
    conn = sqlite3.connect("planner.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            task_time TEXT NOT NULL,
            priority TEXT NOT NULL,
            completed BOOLEAN DEFAULT FALSE,
            user_id INTEGER NOT NULL,
            category TEXT DEFAULT 'general',
            day_of_week TEXT DEFAULT 'monday'
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    return f"{salt}${hashlib.sha256((password + salt).encode()).hexdigest()}"

def verify_password(password: str, hashed_password: str) -> bool:
    if not hashed_password or '$' not in hashed_password:
        return False
    salt, stored_hash = hashed_password.split('$')
    new_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return new_hash == stored_hash

def create_session(user_id: int):
    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = user_id
    return session_id

def get_user_id(request: Request):
    session_id = request.cookies.get("session_id")
    return sessions.get(session_id) if session_id else None

def calculate_progress(tasks):
    if not tasks:
        return {
            'total': 0,
            'completed': 0,
            'percentage': 0,
            'categories': {},
            'days': {}
        }
    
    total = len(tasks)
    completed = sum(1 for task in tasks if task['completed'])
    percentage = round((completed / total * 100), 1) if total > 0 else 0
    
    # Прогресс по категориям
    category_stats = {}
    for cat_key, cat_name in CATEGORIES.items():
        cat_tasks = [t for t in tasks if t['category'] == cat_key]
        cat_total = len(cat_tasks)
        cat_completed = sum(1 for t in cat_tasks if t['completed'])
        cat_percentage = round((cat_completed / cat_total * 100), 1) if cat_total > 0 else 0
        
        category_stats[cat_key] = {
            'name': cat_name,
            'total': cat_total,
            'completed': cat_completed,
            'percentage': cat_percentage
        }
    
    # Прогресс по дням недели
    day_stats = {}
    for day_key, day_name in WEEK_DAYS.items():
        day_tasks = [t for t in tasks if t['day_of_week'] == day_key]
        day_total = len(day_tasks)
        day_completed = sum(1 for t in day_tasks if t['completed'])
        day_percentage = round((day_completed / day_total * 100), 1) if day_total > 0 else 0
        
        day_stats[day_key] = {
            'name': day_name,
            'total': day_total,
            'completed': day_completed,
            'percentage': day_percentage
        }
    
    return {
        'total': total,
        'completed': completed,
        'percentage': percentage,
        'categories': category_stats,
        'days': day_stats
    }

# Инициализируем БД
init_db()

# Главная страница
@app.get("/")
async def home(request: Request):
    user_id = get_user_id(request)
    selected_day = request.query_params.get('day', 'monday')
    
    conn = get_db()
    cursor = conn.cursor()
    
    if user_id:
        cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        username = user['username'] if user else None
        
        # Получаем все задачи пользователя для прогресса
        cursor.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,))
        all_tasks_data = cursor.fetchall()
        all_tasks = [dict(task) for task in all_tasks_data]
        
        # Получаем задачи для выбранного дня
        cursor.execute('SELECT * FROM tasks WHERE user_id = ? AND day_of_week = ? ORDER BY task_time', (user_id, selected_day))
        day_tasks_data = cursor.fetchall()
        day_tasks = [dict(task) for task in day_tasks_data]
        
        progress = calculate_progress(all_tasks)
    else:
        username = None
        day_tasks = []
        progress = calculate_progress([])
    
    return templates.TemplateResponse("index_with_days.html", {
        "request": request,
        "username": username,
        "tasks": day_tasks,
        "selected_day": selected_day,
        "week_days": WEEK_DAYS,
        "categories": CATEGORIES,
        "progress": progress
    })

# Регистрация
@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("simple_register.html", {"request": request})

@app.post("/register")
async def register_user(request: Request, email: str = Form(...), username: str = Form(...), password: str = Form(...)):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        return templates.TemplateResponse("simple_register.html", {
            "request": request,
            "error": "Email уже занят"
        })
    
    password_hash = hash_password(password)
    cursor.execute("INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)", (email, username, password_hash))
    user_id = cursor.lastrowid
    conn.commit()
    
    response = RedirectResponse(url="/", status_code=303)
    session_id = create_session(user_id)
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    
    return response

# Вход
@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("simple_login.html", {"request": request})

@app.post("/login")
async def login_user(request: Request, email: str = Form(...), password: str = Form(...)):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, password_hash FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if not user or not verify_password(password, user['password_hash']):
        return templates.TemplateResponse("simple_login.html", {
            "request": request,
            "error": "Неверный email или пароль"
        })
    
    response = RedirectResponse(url="/", status_code=303)
    session_id = create_session(user['id'])
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    
    return response

# Выход
@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="session_id")
    return response

# Добавление задачи
@app.post("/tasks")
async def add_task(
    request: Request,
    title: str = Form(...),
    task_time: str = Form(...),
    priority: str = Form(...),
    category: str = Form("general"),
    day_of_week: str = Form("monday"),
    description: str = Form("")
):
    user_id = get_user_id(request)
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description, task_time, priority, user_id, category, day_of_week) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (title, description, task_time, priority, user_id, category, day_of_week)
    )
    conn.commit()
    
    return RedirectResponse(url=f"/?day={day_of_week}", status_code=303)

# Обновление статуса задачи
@app.post("/tasks/{task_id}/toggle")
async def toggle_task(task_id: int, request: Request):
    user_id = get_user_id(request)
    if not user_id:
        return {"success": False, "error": "Not authenticated"}
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT completed FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
    task = cursor.fetchone()
    
    if not task:
        return {"success": False, "error": "Task not found"}
    
    new_status = not task['completed']
    cursor.execute("UPDATE tasks SET completed = ? WHERE id = ? AND user_id = ?", (new_status, task_id, user_id))
    conn.commit()
    
    return {"success": True, "completed": new_status}

# Удаление задачи
@app.post("/tasks/{task_id}/delete")
async def delete_task(task_id: int, request: Request):
    user_id = get_user_id(request)
    if not user_id:
        return {"success": False, "error": "Not authenticated"}
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
    conn.commit()
    
    return {"success": True}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
