import streamlit as st
import bcrypt
import json
from datetime import datetime

# Тестовые пользователи (в production используй БД)
TEST_USERS = {
    "admin@ocr.ru": {
        "password_hash": bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode(),
        "user_id": 1,
        "full_name": "Иван Администратор",
        "role": "admin",
        "sports": None  # Все виды спорта
    },
    "curator_athletics@ocr.ru": {
        "password_hash": bcrypt.hashpw(b"curator123", bcrypt.gensalt()).decode(),
        "user_id": 2,
        "full_name": "Сергей Куратор",
        "role": "curator",
        "sports": ["Лёгкая атлетика"]
    },
    "curator_swimming@ocr.ru": {
        "password_hash": bcrypt.hashpw(b"curator123", bcrypt.gensalt()).decode(),
        "user_id": 3,
        "full_name": "Мария Куратор",
        "role": "curator",
        "sports": ["Плавание"]
    },
    "athlete@example.com": {
        "password_hash": bcrypt.hashpw(b"athlete123", bcrypt.gensalt()).decode(),
        "user_id": 100,
        "full_name": "Максим Спортсмен",
        "role": "athlete",
        "sports": None
    }
}


def authenticate_user(email: str, password: str) -> dict | None:
    """Проверка учётных данных пользователя"""
    if email not in TEST_USERS:
        return None
    
    user = TEST_USERS[email]
    if bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
        return {
            "email": email,
            "user_id": user['user_id'],
            "full_name": user['full_name'],
            "role": user['role'],
            "sports": user['sports'],
            "login_time": datetime.now().isoformat()
        }
    
    return None


def init_session_state():
    """Инициализация переменных сессии"""
    if "user" not in st.session_state:
        st.session_state.user = None
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if "selected_athlete" not in st.session_state:
        st.session_state.selected_athlete = None
    
    if "page_state" not in st.session_state:
        st.session_state.page_state = {}


def require_auth(func):
    """Декоратор для проверки аутентификации"""
    def wrapper(*args, **kwargs):
        if not st.session_state.get("authenticated"):
            st.error("❌ Требуется аутентификация")
            return None
        return func(*args, **kwargs)
    return wrapper


def require_role(*allowed_roles):
    """Декоратор для проверки роли"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if st.session_state.get("user") is None:
                st.error("❌ Требуется вход в систему")
                return None
            
            user_role = st.session_state.user.get("role")
            if user_role not in allowed_roles:
                st.error(f"❌ Доступ запрещён. Требуется роль: {', '.join(allowed_roles)}")
                return None
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
