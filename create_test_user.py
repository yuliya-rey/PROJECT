from database.connection import get_db
from utils.auth import hash_password

def create_test_user():
    conn = get_db()
    cursor = conn.cursor()
    
    # Проверяем нет ли уже пользователя
    cursor.execute("SELECT id FROM users WHERE email = ?", ("test@example.com",))
    if cursor.fetchone():
        print("Пользователь уже существует")
        return
    
    # Создаем тестового пользователя
    password_hash = hash_password("123456")
    cursor.execute(
        "INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)",
        ("test@example.com", "testuser", password_hash)
    )
    conn.commit()
    print("Тестовый пользователь создан!")
    print("Email: test@example.com")
    print("Пароль: 123456")

if __name__ == "__main__":
    create_test_user()
