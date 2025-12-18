from main import get_db, hash_password

def create_test_user():
    conn = get_db()
    cursor = conn.cursor()
    
    # Проверяем нет ли уже пользователя
    cursor.execute("SELECT id FROM users WHERE email = ?", ("test@test.com",))
    if cursor.fetchone():
        print("✅ Пользователь уже существует")
        return
    
    # Создаем тестового пользователя
    password_hash = hash_password("123")
    cursor.execute(
        "INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)",
        ("test@test.com", "testuser", password_hash)
    )
    
    # Добавляем тестовые задачи
    user_id = cursor.lastrowid
    
    # Задачи на понедельник
    cursor.execute(
        "INSERT INTO tasks (title, task_time, priority, user_id, category, day_of_week) VALUES (?, ?, ?, ?, ?, ?)",
        ("Утренняя зарядка", "08:00", "medium", user_id, "health", "monday")
    )
    cursor.execute(
        "INSERT INTO tasks (title, task_time, priority, user_id, category, day_of_week) VALUES (?, ?, ?, ?, ?, ?)",
        ("Работа над проектом", "10:00", "high", user_id, "work", "monday")
    )
    
    # Задачи на вторник
    cursor.execute(
        "INSERT INTO tasks (title, task_time, priority, user_id, category, day_of_week) VALUES (?, ?, ?, ?, ?, ?)",
        ("Изучение Python", "09:00", "high", user_id, "study", "tuesday")
    )
    
    # Задачи на среду
    cursor.execute(
        "INSERT INTO tasks (title, task_time, priority, user_id, category, day_of_week) VALUES (?, ?, ?, ?, ?, ?)",
        ("Встреча с друзьями", "19:00", "low", user_id, "general", "wednesday")
    )
    
    conn.commit()
    print("✅ Тестовый пользователь создан!")
    print("📧 Email: test@test.com")
    print("🔑 Пароль: 123")
    print("📝 Добавлено 4 тестовые задачи на разные дни")

if __name__ == "__main__":
    create_test_user()
