"""
Модуль аутентификации для веб-приложения Streamlit
Цифровой реестр олимпийского резерва
"""

import streamlit as st
import pandas as pd
import bcrypt
from utils.database import get_db_connection

# Константы по умолчанию
DEFAULT_USERS = {
    'admin': {
        'password': 'admin123',
        'role': 'admin',
        'username': 'admin'
    },
    'curator_ski': {
        'password': 'curator123',
        'role': 'curator',
        'username': 'curator_ski',
        'sport_id': 1,
        'sport_name': 'Лыжные гонки'
    },
    'ivanov_a': {
        'password': 'athlete123',
        'role': 'athlete',
        'username': 'ivanov_a',
        'athlete_id': 1
    }
}

def hash_password(password: str) -> str:
    """
    Хэширование пароля с помощью bcrypt
    
    Args:
        password: Исходный пароль
    
    Returns:
        Хэшированный пароль
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """
    Проверка пароля
    
    Args:
        password: Пароль для проверки
        hashed: Хэшированный пароль
    
    Returns:
        True если пароль совпадает, иначе False
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

def authenticate_user(username: str, password: str) -> bool:
    """
    Аутентификация пользователя
    
    Args:
        username: Логин
        password: Пароль
    
    Returns:
        True если аутентификация успешна, иначе False
    """
    try:
        conn = get_db_connection()
        
        # Попытка получить пользователя из БД
        query = "SELECT username, password_hash, role, sport_id FROM users WHERE username = %s"
        result = pd.read_sql(query, conn, params=(username,))
        conn.close()
        
        if not result.empty:
            user_record = result.iloc[0]
            # Проверяем пароль
            if verify_password(password, user_record['password_hash']):
                # Сохраняем данные пользователя в session
                st.session_state.user = {
                    'username': user_record['username'],
                    'role': user_record['role'],
                    'sport_id': user_record['sport_id'],
                    'authenticated': True
                }
                return True
    except Exception:
        # Если ошибка БД, используем тестовые учетные данные
        pass
    
    # Проверяем в тестовых учетных данных
    if username in DEFAULT_USERS:
        user_data = DEFAULT_USERS[username]
        if user_data['password'] == password:  # В демо просто сравниваем
            st.session_state.user = {
                'username': username,
                'role': user_data['role'],
                'sport_id': user_data.get('sport_id'),
                'sport_name': user_data.get('sport_name'),
                'athlete_id': user_data.get('athlete_id'),
                'authenticated': True
            }
            return True
    
    return False

def check_authentication() -> bool:
    """
    Проверка аутентификации пользователя
    
    Returns:
        True если пользователь аутентифицирован, иначе False
    """
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    return st.session_state.user is not None and st.session_state.user.get('authenticated', False)

def get_current_user() -> dict:
    """
    Получение текущего пользователя
    
    Returns:
        Словарь с данными пользователя
    """
    if 'user' not in st.session_state or st.session_state.user is None:
        return {
            'username': 'Unknown',
            'role': 'guest',
            'authenticated': False
        }
    
    return st.session_state.user

def logout_user():
    """
    Выход пользователя из системы
    """
    if 'user' in st.session_state:
        st.session_state.user = None
    
    # Очищаем все данные сессии
    for key in list(st.session_state.keys()):
        if key != '_streamlit_script_run_ctx':
            del st.session_state[key]

def has_permission(required_role: str) -> bool:
    """
    Проверка прав доступа
    
    Args:
        required_role: Требуемая роль (admin, curator, athlete)
    
    Returns:
        True если у пользователя есть необходимые права
    """
    user = get_current_user()
    
    if not user.get('authenticated', False):
        return False
    
    user_role = user.get('role', 'guest')
    
    # Иерархия ролей: admin > curator > athlete
    role_hierarchy = {
        'admin': 3,
        'curator': 2,
        'athlete': 1,
        'guest': 0
    }
    
    return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)

def require_login(func):
    """
    Декоратор для требования входа в систему
    
    Args:
        func: Функция для обертки
    
    Returns:
        Обернутая функция
    """
    def wrapper(*args, **kwargs):
        if not check_authentication():
            st.warning("⚠️ Необходима аутентификация")
            st.stop()
        return func(*args, **kwargs)
    
    return wrapper

def require_role(required_role: str):
    """
    Декоратор для требования определенной роли
    
    Args:
        required_role: Требуемая роль
    
    Returns:
        Функция-декоратор
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not check_authentication():
                st.warning("⚠️ Необходима аутентификация")
                st.stop()
            
            if not has_permission(required_role):
                st.error(f"❌ Для этой операции требуется роль: {required_role}")
                st.stop()
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator

def get_user_by_id(user_id: int) -> dict:
    """
    Получение пользователя по ID
    
    Args:
        user_id: ID пользователя
    
    Returns:
        Словарь с данными пользователя
    """
    try:
        conn = get_db_connection()
        query = "SELECT * FROM users WHERE id = %s"
        result = pd.read_sql(query, conn, params=(user_id,))
        conn.close()
        
        if not result.empty:
            return result.iloc[0].to_dict()
    except Exception as e:
        st.error(f"Ошибка получения пользователя: {e}")
    
    return None

def register_user(username: str, password: str, role: str = 'athlete', sport_id: int = None) -> bool:
    """
    Регистрация нового пользователя (для администратора)
    
    Args:
        username: Логин
        password: Пароль
        role: Роль (admin, curator, athlete)
        sport_id: ID вида спорта (для куратора)
    
    Returns:
        True если регистрация успешна
    """
    try:
        conn = get_db_connection()
        
        # Проверяем что пользователя нет
        check_query = "SELECT id FROM users WHERE username = %s"
        exists = pd.read_sql(check_query, conn, params=(username,))
        
        if not exists.empty:
            st.error(f"Пользователь {username} уже существует")
            return False
        
        # Хэшируем пароль
        password_hash = hash_password(password)
        
        # Вставляем пользователя
        insert_query = """
        INSERT INTO users (username, password_hash, role, sport_id)
        VALUES (%s, %s, %s, %s)
        """
        
        cursor = conn.cursor()
        cursor.execute(insert_query, (username, password_hash, role, sport_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        st.success(f"✅ Пользователь {username} успешно зарегистрирован")
        return True
    
    except Exception as e:
        st.error(f"Ошибка регистрации: {e}")
        return False

def update_password(username: str, old_password: str, new_password: str) -> bool:
    """
    Обновление пароля пользователя
    
    Args:
        username: Логин
        old_password: Старый пароль
        new_password: Новый пароль
    
    Returns:
        True если пароль обновлен успешно
    """
    try:
        # Сначала проверяем старый пароль
        if not authenticate_user(username, old_password):
            st.error("❌ Неверный текущий пароль")
            return False
        
        conn = get_db_connection()
        
        # Хэшируем новый пароль
        new_hash = hash_password(new_password)
        
        # Обновляем пароль
        update_query = "UPDATE users SET password_hash = %s WHERE username = %s"
        cursor = conn.cursor()
        cursor.execute(update_query, (new_hash, username))
        conn.commit()
        cursor.close()
        conn.close()
        
        st.success("✅ Пароль успешно обновлен")
        return True
    
    except Exception as e:
        st.error(f"Ошибка обновления пароля: {e}")
        return False

def init_session_state():
    """
    Инициализация состояния сессии Streamlit
    """
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
