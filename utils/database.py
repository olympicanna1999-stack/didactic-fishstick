"""
Модуль работы с базой данных PostgreSQL (БЕЗ SECRETS - ПАРАМЕТРЫ В КОДЕ)
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

# ====== ПАРАМЕТРЫ ПОДКЛЮЧЕНИЯ (вставь свои!) ======
DB_CONFIG = {
    'host': 'db.bssbrxzbljzanponotmc.supabase.co',
    'port': 5432,
    'database': 'postgres',
    'username': 'postgres',
    'password': 'ВСТАВЬ_ПАРОЛЬ',
}

@st.cache_resource
def get_db_connection():
    """Получение подключения к PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['username'],
            password=DB_CONFIG['password'],
            connect_timeout=10
        )
        return conn
    except Exception as e:
        st.error(f"Ошибка подключения: {e}")
        st.stop()

def execute_query(query: str, params=None):
    """Выполнение SQL запроса"""
    try:
        conn = get_db_connection()
        if params:
            result = pd.read_sql(query, conn, params=params)
        else:
            result = pd.read_sql(query, conn)
        conn.close()
        return result
    except Exception as e:
        st.error(f"Ошибка запроса: {e}")
        return pd.DataFrame()

def init_database():
    """Инициализация таблиц если их нет"""
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Таблица спортсменов
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS athletes (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            birth_date DATE,
            program_status VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Таблица результатов
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sport_results (
            id SERIAL PRIMARY KEY,
            athlete_id INTEGER REFERENCES athletes(id),
            competition_name VARCHAR(200),
            result VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Ошибка инициализации: {e}")
        return False

def get_athletes():
    """Получение списка спортсменов"""
    query = "SELECT * FROM athletes ORDER BY last_name, first_name"
    return execute_query(query)

def get_athlete_by_id(athlete_id: int):
    """Получение спортсмена по ID"""
    query = "SELECT * FROM athletes WHERE id = %s"
    return execute_query(query, [athlete_id])

def get_sport_results(athlete_id=None):
    """Получение спортивных результатов"""
    if athlete_id:
        query = "SELECT * FROM sport_results WHERE athlete_id = %s ORDER BY created_at DESC"
        return execute_query(query, [athlete_id])
    else:
        query = "SELECT * FROM sport_results ORDER BY created_at DESC LIMIT 50"
        return execute_query(query)

def get_medical_data(athlete_id: int):
    """Получение медицинских данных"""
    query = "SELECT * FROM athletes WHERE id = %s"
    return execute_query(query, [athlete_id])

def get_functional_tests(athlete_id: int):
    """Получение функциональных тестов"""
    query = "SELECT * FROM athletes WHERE id = %s"
    return execute_query(query, [athlete_id])

def get_sports():
    """Получение видов спорта"""
    return pd.DataFrame({'id': [1, 2, 3], 'name': ['Лыжные гонки', 'Биатлон', 'Гребля']})

def get_regions():
    """Получение регионов"""
    return pd.DataFrame({'id': [1, 2, 3], 'name': ['Москва', 'СПб', 'Екатеринбург']})
