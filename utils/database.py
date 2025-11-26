"""
Модуль работы с базой данных SQLite (ЛОКАЛЬНАЯ БД - БЕЗ ИНТЕРНЕТА)
ИСПРАВЛЕННАЯ ВЕРСИЯ: Без проблем с threading

ПРЕИМУЩЕСТВА:
✅ Работает БЕЗ интернета
✅ Нет нужды в пароле
✅ Нет ошибок подключения
✅ Быстрее чем Supabase
✅ Все работает локально
✅ Исправлены проблемы с threading
"""

import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
import bcrypt

# Путь к БД (в папке проекта)
DB_PATH = Path('olympic_reserve.db')

def get_db_connection():
    """Получение подключения к SQLite (БЕЗ кэширования!)"""
    try:
        # ВАЖНО: Не используем @st.cache_resource для sqlite3
        # так как это вызывает проблемы с threading
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        st.error(f"❌ Ошибка подключения к БД: {e}")
        return None

def execute_query(query: str, params=None):
    """Выполнение SELECT запроса"""
    try:
        conn = get_db_connection()
        if conn is None:
            return pd.DataFrame()
        
        if params:
            df = pd.read_sql(query, conn, params=params)
        else:
            df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Ошибка запроса: {e}")
        return pd.DataFrame()

def execute_update(query: str, params=None):
    """Выполнение UPDATE/INSERT/DELETE"""
    try:
        conn = get_db_connection()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ Ошибка: {e}")
        return False

def init_database():
    """Инициализация БД - создаёт таблицы и добавляет тестовые данные"""
    try:
        conn = get_db_connection()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        
        # 1. Таблица пользователей
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # 2. Таблица спортсменов
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS athletes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            birth_date DATE,
            gender TEXT,
            program_status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # 3. Таблица результатов соревнований
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sport_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            athlete_id INTEGER NOT NULL,
            competition_name TEXT,
            competition_date DATE,
            discipline TEXT,
            result TEXT,
            place INTEGER,
            is_personal_best BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(athlete_id) REFERENCES athletes(id)
        );
        """)
        
        # 4. Таблица функциональных тестов
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS functional_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            athlete_id INTEGER NOT NULL,
            test_date DATE,
            vo2_max_relative REAL,
            pano_threshold REAL,
            max_hr INTEGER,
            resting_hr INTEGER,
            weight_kg REAL,
            body_fat_percent REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(athlete_id) REFERENCES athletes(id)
        );
        """)
        
        # 5. Таблица медицинских данных
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS medical_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            athlete_id INTEGER NOT NULL,
            examination_date DATE,
            hemoglobin_g_l REAL,
            hematocrit_percent REAL,
            cleared_for_training BOOLEAN DEFAULT 1,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(athlete_id) REFERENCES athletes(id)
        );
        """)
        
        # 6. Таблица планов развития
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS development_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            athlete_id INTEGER NOT NULL,
            plan_date DATE,
            goals TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(athlete_id) REFERENCES athletes(id)
        );
        """)
        
        # 7. Таблица видов спорта
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT
        );
        """)
        
        # 8. Таблица регионов
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS regions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
        """)
        
        conn.commit()
        
        # Проверяем есть ли уже данные
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            # Добавляем тестовые пользователи
            admin_hash = bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode()
            curator_hash = bcrypt.hashpw(b'curator123', bcrypt.gensalt()).decode()
            athlete_hash = bcrypt.hashpw(b'athlete123', bcrypt.gensalt()).decode()
            
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                ('admin', admin_hash, 'admin')
            )
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                ('curator_ski', curator_hash, 'curator')
            )
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                ('ivanov_a', athlete_hash, 'athlete')
            )
            
            # Добавляем виды спорта
            sports = [
                ('Лыжные гонки', 'Циклический зимний вид спорта'),
                ('Биатлон', 'Циклический вид спорта со стрельбой'),
                ('Конькобежный спорт', 'Зимний циклический вид спорта'),
                ('Академическая гребля', 'Водный вид спорта'),
            ]
            
            for name, desc in sports:
                cursor.execute(
                    "INSERT OR IGNORE INTO sports (name, description) VALUES (?, ?)",
                    (name, desc)
                )
            
            # Добавляем регионы
            regions = ['Московская область', 'Санкт-Петербург', 'Екатеринбург', 'Новосибирск']
            
            for region in regions:
                cursor.execute(
                    "INSERT OR IGNORE INTO regions (name) VALUES (?)",
                    (region,)
                )
            
            # Добавляем тестовых спортсменов
            cursor.execute(
                """INSERT INTO athletes 
                   (first_name, last_name, birth_date, gender, program_status) 
                   VALUES (?, ?, ?, ?, ?)""",
                ('Иван', 'Иванов', '2005-01-15', 'М', 'active')
            )
            cursor.execute(
                """INSERT INTO athletes 
                   (first_name, last_name, birth_date, gender, program_status) 
                   VALUES (?, ?, ?, ?, ?)""",
                ('Анна', 'Петрова', '2004-03-22', 'Ж', 'active')
            )
            cursor.execute(
                """INSERT INTO athletes 
                   (first_name, last_name, birth_date, gender, program_status) 
                   VALUES (?, ?, ?, ?, ?)""",
                ('Дмитрий', 'Сидоров', '2006-07-10', 'М', 'active')
            )
            
            conn.commit()
        
        cursor.close()
        conn.close()
        
        return True
    
    except Exception as e:
        st.error(f"❌ Ошибка инициализации БД: {e}")
        return False

# ==================== ФУНКЦИИ ДЛЯ СПОРТСМЕНОВ ====================

def get_athletes(status='active'):
    """Получение списка спортсменов"""
    query = "SELECT * FROM athletes WHERE program_status = ? ORDER BY last_name, first_name"
    return execute_query(query, [status])

def get_athlete_by_id(athlete_id: int):
    """Получение спортсмена по ID"""
    query = "SELECT * FROM athletes WHERE id = ?"
    return execute_query(query, [athlete_id])

def add_athlete(first_name, last_name, birth_date, gender, status='active'):
    """Добавление нового спортсмена"""
    query = """INSERT INTO athletes 
               (first_name, last_name, birth_date, gender, program_status)
               VALUES (?, ?, ?, ?, ?)"""
    return execute_update(query, (first_name, last_name, birth_date, gender, status))

# ==================== ФУНКЦИИ ДЛЯ РЕЗУЛЬТАТОВ ====================

def get_sport_results(athlete_id=None, limit=50):
    """Получение спортивных результатов"""
    if athlete_id:
        query = f"SELECT * FROM sport_results WHERE athlete_id = ? ORDER BY competition_date DESC LIMIT {limit}"
        return execute_query(query, [athlete_id])
    else:
        query = f"SELECT * FROM sport_results ORDER BY competition_date DESC LIMIT {limit}"
        return execute_query(query)

def add_sport_result(athlete_id, competition_name, competition_date, discipline, result, place):
    """Добавление результата"""
    query = """INSERT INTO sport_results 
               (athlete_id, competition_name, competition_date, discipline, result, place)
               VALUES (?, ?, ?, ?, ?, ?)"""
    return execute_update(query, (athlete_id, competition_name, competition_date, discipline, result, place))

# ==================== ФУНКЦИИ ДЛЯ МЕДИЦИНСКИХ ДАННЫХ ====================

def get_medical_data(athlete_id: int):
    """Получение медицинских данных"""
    query = "SELECT * FROM medical_data WHERE athlete_id = ? ORDER BY examination_date DESC"
    return execute_query(query, [athlete_id])

def get_functional_tests(athlete_id: int):
    """Получение функциональных тестов"""
    query = "SELECT * FROM functional_tests WHERE athlete_id = ? ORDER BY test_date DESC"
    return execute_query(query, [athlete_id])

# ==================== ФУНКЦИИ ДЛЯ СПРАВОЧНИКОВ ====================

def get_sports():
    """Получение видов спорта"""
    query = "SELECT * FROM sports ORDER BY name"
    return execute_query(query)

def get_regions():
    """Получение регионов"""
    query = "SELECT * FROM regions ORDER BY name"
    return execute_query(query)

# ==================== ФУНКЦИИ ДЛЯ СТАТИСТИКИ ====================

def get_athlete_statistics(athlete_id: int):
    """Получение статистики спортсмена"""
    stats = {}
    
    comps = execute_query("SELECT COUNT(*) as count FROM sport_results WHERE athlete_id = ?", [athlete_id])
    stats['total_competitions'] = comps['count'][0] if not comps.empty else 0
    
    pbs = execute_query("SELECT COUNT(*) as count FROM sport_results WHERE athlete_id = ? AND is_personal_best = 1", [athlete_id])
    stats['personal_bests'] = pbs['count'][0] if not pbs.empty else 0
    
    places = execute_query("SELECT AVG(place) as avg_place FROM sport_results WHERE athlete_id = ?", [athlete_id])
    stats['avg_place'] = round(places['avg_place'][0], 2) if not places.empty and places['avg_place'][0] else None
    
    return stats

def get_user_by_username(username: str):
    """Получение пользователя по логину"""
    query = "SELECT * FROM users WHERE username = ?"
    result = execute_query(query, [username])
    return result.to_dict('records')[0] if not result.empty else None

def get_total_athletes():
    """Общее количество спортсменов"""
    result = execute_query("SELECT COUNT(*) as count FROM athletes WHERE program_status = 'active'")
    return result['count'][0] if not result.empty else 0

def get_total_competitions():
    """Общее количество соревнований"""
    result = execute_query("SELECT COUNT(*) as count FROM sport_results")
    return result['count'][0] if not result.empty else 0
