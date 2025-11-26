"""
Модуль работы с базой данных PostgreSQL
Цифровой реестр олимпийского резерва
"""

import streamlit as st
import pandas as pd
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

@st.cache_resource
def get_db_connection():
    """
    Получение подключения к PostgreSQL с кэшированием
    
    Returns:
        Подключение к БД (psycopg2 connection object)
    """
    try:
        # Пытаемся получить параметры из secrets.toml (Streamlit Cloud)
        if hasattr(st, 'secrets') and 'connections' in st.secrets:
            db_config = st.secrets.connections.postgresql
            conn = psycopg2.connect(
                host=db_config.get('host'),
                port=db_config.get('port', 5432),
                database=db_config.get('database'),
                user=db_config.get('username'),
                password=db_config.get('password')
            )
        else:
            # Иначе используем переменные окружения или значения по умолчанию
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', 5432)),
                database=os.getenv('DB_NAME', 'olympic_reserve'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', '')
            )
        
        return conn
    
    except psycopg2.OperationalError as e:
        st.error(f"""
        ❌ Ошибка подключения к БД: {str(e)[:100]}
        
        **Проверьте:**
        1. Доступность сервера БД
        2. Правильность параметров в secrets.toml или .env
        3. Правильность логина/пароля
        
        **Параметры подключения:**
        - Host: {os.getenv('DB_HOST', 'localhost')}
        - Port: {os.getenv('DB_PORT', 5432)}
        - Database: {os.getenv('DB_NAME', 'olympic_reserve')}
        """)
        st.stop()
    
    except Exception as e:
        st.error(f"❌ Неожиданная ошибка: {e}")
        st.stop()

def execute_query(query: str, params=None):
    """
    Выполнение SQL запроса и получение результата в виде DataFrame
    
    Args:
        query: SQL запрос
        params: Параметры для подстановки в запрос (опционально)
    
    Returns:
        pandas DataFrame с результатами
    """
    try:
        conn = get_db_connection()
        
        if params:
            result = pd.read_sql(query, conn, params=params)
        else:
            result = pd.read_sql(query, conn)
        
        conn.close()
        return result
    
    except Exception as e:
        st.error(f"Ошибка выполнения запроса: {e}")
        return pd.DataFrame()

def init_database():
    """
    Инициализация базы данных при первом запуске
    Создает таблицы если их нет
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL,
            sport_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Таблица видов спорта
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sports (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            description TEXT
        );
        """)
        
        # Таблица регионов
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS regions (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL
        );
        """)
        
        # Таблица спортсменов
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS athletes (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            birth_date DATE,
            gender VARCHAR(10),
            sport_id INTEGER REFERENCES sports(id),
            region_id INTEGER REFERENCES regions(id),
            program_status VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Таблица спортивных результатов
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sport_results (
            id SERIAL PRIMARY KEY,
            athlete_id INTEGER REFERENCES athletes(id),
            competition_name VARCHAR(200),
            competition_date DATE,
            discipline VARCHAR(100),
            result VARCHAR(100),
            place INTEGER,
            is_personal_best BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Таблица функциональных тестов
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS functional_tests (
            id SERIAL PRIMARY KEY,
            athlete_id INTEGER REFERENCES athletes(id),
            test_date DATE,
            vo2_max_relative FLOAT,
            pano_threshold FLOAT,
            max_hr INTEGER,
            resting_hr INTEGER,
            weight_kg FLOAT,
            body_fat_percent FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Таблица медицинских данных
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS medical_data (
            id SERIAL PRIMARY KEY,
            athlete_id INTEGER REFERENCES athletes(id),
            examination_date DATE,
            hemoglobin_g_l FLOAT,
            hematocrit_percent FLOAT,
            cleared_for_training BOOLEAN DEFAULT TRUE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Таблица планов развития
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS development_plans (
            id SERIAL PRIMARY KEY,
            athlete_id INTEGER REFERENCES athletes(id),
            plan_date DATE,
            goals TEXT,
            status VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Таблица документов
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            athlete_id INTEGER REFERENCES athletes(id),
            document_type VARCHAR(100),
            file_path VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
    
    except Exception as e:
        st.error(f"Ошибка инициализации БД: {e}")
        return False

# ==================== ФУНКЦИИ ДЛЯ СПОРТСМЕНОВ ====================

def get_athletes(sport_id=None, region_id=None, status='active'):
    """
    Получение списка спортсменов
    
    Args:
        sport_id: ID вида спорта (опционально)
        region_id: ID региона (опционально)
        status: Статус программы (по умолчанию 'active')
    
    Returns:
        DataFrame со списком спортсменов
    """
    query = "SELECT * FROM athletes WHERE program_status = %s"
    params = [status]
    
    if sport_id:
        query += " AND sport_id = %s"
        params.append(sport_id)
    
    if region_id:
        query += " AND region_id = %s"
        params.append(region_id)
    
    query += " ORDER BY last_name, first_name"
    
    return execute_query(query, params)

def get_athlete_by_id(athlete_id: int):
    """
    Получение спортсмена по ID
    
    Args:
        athlete_id: ID спортсмена
    
    Returns:
        DataFrame с данными спортсмена
    """
    query = """
    SELECT a.*, s.name as sport_name, r.name as region_name
    FROM athletes a
    LEFT JOIN sports s ON a.sport_id = s.id
    LEFT JOIN regions r ON a.region_id = r.id
    WHERE a.id = %s
    """
    return execute_query(query, [athlete_id])

# ==================== ФУНКЦИИ ДЛЯ РЕЗУЛЬТАТОВ ====================

def get_sport_results(athlete_id=None, sport_id=None, limit=50):
    """
    Получение спортивных результатов
    
    Args:
        athlete_id: ID спортсмена (опционально)
        sport_id: ID вида спорта (опционально)
        limit: Максимальное количество записей
    
    Returns:
        DataFrame с результатами
    """
    query = "SELECT * FROM sport_results WHERE 1=1"
    params = []
    
    if athlete_id:
        query += " AND athlete_id = %s"
        params.append(athlete_id)
    
    if sport_id:
        query += " AND athlete_id IN (SELECT id FROM athletes WHERE sport_id = %s)"
        params.append(sport_id)
    
    query += f" ORDER BY competition_date DESC LIMIT {limit}"
    
    return execute_query(query, params)

def add_sport_result(athlete_id: int, competition_name: str, competition_date: str, 
                    discipline: str, result: str, place: int, is_personal_best=False):
    """
    Добавление нового спортивного результата
    
    Args:
        athlete_id: ID спортсмена
        competition_name: Название соревнования
        competition_date: Дата соревнования
        discipline: Дисциплина
        result: Результат
        place: Место
        is_personal_best: Личный рекорд?
    
    Returns:
        True если успешно, иначе False
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO sport_results 
        (athlete_id, competition_name, competition_date, discipline, result, place, is_personal_best)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (athlete_id, competition_name, competition_date, 
                              discipline, result, place, is_personal_best))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
    
    except Exception as e:
        st.error(f"Ошибка добавления результата: {e}")
        return False

# ==================== ФУНКЦИИ ДЛЯ ФУНКЦИОНАЛЬНЫХ ТЕСТОВ ====================

def get_functional_tests(athlete_id: int, limit=50):
    """
    Получение функциональных тестов спортсмена
    
    Args:
        athlete_id: ID спортсмена
        limit: Максимальное количество записей
    
    Returns:
        DataFrame с тестами
    """
    query = f"""
    SELECT * FROM functional_tests
    WHERE athlete_id = %s
    ORDER BY test_date DESC
    LIMIT {limit}
    """
    return execute_query(query, [athlete_id])

# ==================== ФУНКЦИИ ДЛЯ МЕДИЦИНСКИХ ДАННЫХ ====================

def get_medical_data(athlete_id: int, limit=50):
    """
    Получение медицинских данных спортсмена
    
    Args:
        athlete_id: ID спортсмена
        limit: Максимальное количество записей
    
    Returns:
        DataFrame с медицинскими данными
    """
    query = f"""
    SELECT * FROM medical_data
    WHERE athlete_id = %s
    ORDER BY examination_date DESC
    LIMIT {limit}
    """
    return execute_query(query, [athlete_id])

# ==================== ФУНКЦИИ ДЛЯ СПРАВОЧНИКОВ ====================

def get_sports():
    """
    Получение списка видов спорта
    
    Returns:
        DataFrame со списком видов спорта
    """
    query = "SELECT * FROM sports ORDER BY name"
    return execute_query(query)

def get_regions():
    """
    Получение списка регионов
    
    Returns:
        DataFrame со списком регионов
    """
    query = "SELECT * FROM regions ORDER BY name"
    return execute_query(query)

def get_development_plans(athlete_id: int):
    """
    Получение планов развития спортсмена
    
    Args:
        athlete_id: ID спортсмена
    
    Returns:
        DataFrame с планами
    """
    query = """
    SELECT * FROM development_plans
    WHERE athlete_id = %s
    ORDER BY plan_date DESC
    """
    return execute_query(query, [athlete_id])

def get_documents(athlete_id: int):
    """
    Получение документов спортсмена
    
    Args:
        athlete_id: ID спортсмена
    
    Returns:
        DataFrame с документами
    """
    query = """
    SELECT * FROM documents
    WHERE athlete_id = %s
    ORDER BY created_at DESC
    """
    return execute_query(query, [athlete_id])

# ==================== ФУНКЦИИ ДЛЯ СТАТИСТИКИ ====================

def get_athlete_statistics(athlete_id: int):
    """
    Получение статистики спортсмена
    
    Args:
        athlete_id: ID спортсмена
    
    Returns:
        Словарь со статистикой
    """
    stats = {}
    
    # Всего соревнований
    comps = execute_query("SELECT COUNT(*) as count FROM sport_results WHERE athlete_id = %s", [athlete_id])
    stats['total_competitions'] = comps['count'][0] if not comps.empty else 0
    
    # Личных рекордов
    pbs = execute_query("SELECT COUNT(*) as count FROM sport_results WHERE athlete_id = %s AND is_personal_best = TRUE", [athlete_id])
    stats['personal_bests'] = pbs['count'][0] if not pbs.empty else 0
    
    # Средний результат (место)
    places = execute_query("SELECT AVG(place) as avg_place FROM sport_results WHERE athlete_id = %s", [athlete_id])
    stats['avg_place'] = round(places['avg_place'][0], 2) if not places.empty and places['avg_place'][0] else None
    
    return stats

def get_sport_statistics(sport_id: int):
    """
    Получение статистики по виду спорта
    
    Args:
        sport_id: ID вида спорта
    
    Returns:
        Словарь со статистикой
    """
    stats = {}
    
    # Всего спортсменов
    athletes_count = execute_query(
        "SELECT COUNT(*) as count FROM athletes WHERE sport_id = %s AND program_status = 'active'",
        [sport_id]
    )
    stats['total_athletes'] = athletes_count['count'][0] if not athletes_count.empty else 0
    
    # Всего результатов
    results_count = execute_query(
        """SELECT COUNT(*) as count FROM sport_results sr
           JOIN athletes a ON sr.athlete_id = a.id
           WHERE a.sport_id = %s""",
        [sport_id]
    )
    stats['total_results'] = results_count['count'][0] if not results_count.empty else 0
    
    return stats
