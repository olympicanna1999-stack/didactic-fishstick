"""
Скрипт инициализации базы данных Supabase
Создаёт все необходимые таблицы при первом запуске

Использование:
    python scripts/init_database.py
или добавить вызов в app.py при первом запуске
"""

import sys
import os
from pathlib import Path

# Добавляем корневую папку в path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import psycopg2
from psycopg2 import sql
import bcrypt

# Параметры подключения к Supabase
DB_CONFIG = {
    'host': 'db.bssbrxzbljzanponotmc.supabase.co',
    'port': 5432,
    'database': 'postgres',
    'username': 'postgres',
    'password': 'Rqyd6a6luT0k35oG',  # ← ЗАМЕНИ!
}

def create_tables():
    """Создаёт все необходимые таблицы в БД"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['username'],
            password=DB_CONFIG['password'],
            connect_timeout=10
        )
        cursor = conn.cursor()
        
        print("📊 Создание таблиц в Supabase...")
        
        # 1. Таблица видов спорта
        print("  ✓ Создание таблицы sports...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sports (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            description TEXT
        );
        """)
        
        # 2. Таблица регионов
        print("  ✓ Создание таблицы regions...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS regions (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL
        );
        """)
        
        # 3. Таблица пользователей
        print("  ✓ Создание таблицы users...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL,
            sport_id INTEGER REFERENCES sports(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # 4. Таблица спортсменов
        print("  ✓ Создание таблицы athletes...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS athletes (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            birth_date DATE,
            gender VARCHAR(10),
            sport_id INTEGER REFERENCES sports(id),
            region_id INTEGER REFERENCES regions(id),
            program_status VARCHAR(50) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # 5. Таблица спортивных результатов
        print("  ✓ Создание таблицы sport_results...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sport_results (
            id SERIAL PRIMARY KEY,
            athlete_id INTEGER REFERENCES athletes(id) ON DELETE CASCADE,
            competition_name VARCHAR(200),
            competition_date DATE,
            discipline VARCHAR(100),
            result VARCHAR(100),
            place INTEGER,
            is_personal_best BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # 6. Таблица функциональных тестов
        print("  ✓ Создание таблицы functional_tests...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS functional_tests (
            id SERIAL PRIMARY KEY,
            athlete_id INTEGER REFERENCES athletes(id) ON DELETE CASCADE,
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
        
        # 7. Таблица медицинских данных
        print("  ✓ Создание таблицы medical_data...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS medical_data (
            id SERIAL PRIMARY KEY,
            athlete_id INTEGER REFERENCES athletes(id) ON DELETE CASCADE,
            examination_date DATE,
            hemoglobin_g_l FLOAT,
            hematocrit_percent FLOAT,
            cleared_for_training BOOLEAN DEFAULT TRUE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # 8. Таблица планов развития
        print("  ✓ Создание таблицы development_plans...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS development_plans (
            id SERIAL PRIMARY KEY,
            athlete_id INTEGER REFERENCES athletes(id) ON DELETE CASCADE,
            plan_date DATE,
            goals TEXT,
            status VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # 9. Таблица документов
        print("  ✓ Создание таблицы documents...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            athlete_id INTEGER REFERENCES athletes(id) ON DELETE CASCADE,
            document_type VARCHAR(100),
            file_path VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        conn.commit()
        print("\n✅ Все таблицы созданы успешно!\n")
        
        # Вставляем тестовые данные
        insert_test_data(cursor, conn)
        
        cursor.close()
        conn.close()
        
        return True
    
    except psycopg2.Error as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка создания таблиц: {e}")
        return False

def insert_test_data(cursor, conn):
    """Вставляет тестовые данные для демонстрации"""
    try:
        print("📝 Вставка тестовых данных...\n")
        
        # Виды спорта
        print("  ✓ Добавление видов спорта...")
        sports = [
            ('Лыжные гонки', 'Зимний циклический вид спорта'),
            ('Биатлон', 'Циклический вид спорта с элементами стрельбы'),
            ('Конькобежный спорт', 'Зимний циклический вид спорта'),
            ('Академическая гребля', 'Водный вид спорта'),
            ('Спортивная гимнастика', 'Гимнастический вид спорта'),
        ]
        
        for name, description in sports:
            cursor.execute(
                "INSERT INTO sports (name, description) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                (name, description)
            )
        
        # Регионы
        print("  ✓ Добавление регионов...")
        regions = [
            'Московская область',
            'Санкт-Петербург',
            'Екатеринбург',
            'Новосибирск',
            'Краснодар',
        ]
        
        for region in regions:
            cursor.execute(
                "INSERT INTO regions (name) VALUES (%s) ON CONFLICT DO NOTHING;",
                (region,)
            )
        
        # Тестовые пользователи
        print("  ✓ Добавление тестовых пользователей...")
        
        # Хэшируем пароли
        admin_password = bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode()
        curator_password = bcrypt.hashpw(b'curator123', bcrypt.gensalt()).decode()
        athlete_password = bcrypt.hashpw(b'athlete123', bcrypt.gensalt()).decode()
        
        users = [
            ('admin', admin_password, 'admin', None),
            ('curator_ski', curator_password, 'curator', 1),  # Куратор лыжных гонок
            ('ivanov_a', athlete_password, 'athlete', 1),     # Спортсмен
        ]
        
        for username, password, role, sport_id in users:
            cursor.execute(
                """INSERT INTO users (username, password_hash, role, sport_id) 
                   VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING;""",
                (username, password, role, sport_id)
            )
        
        # Тестовые спортсмены
        print("  ✓ Добавление тестовых спортсменов...")
        athletes = [
            ('Иван', 'Иванов', '2005-01-15', 'М', 1, 1, 'active'),
            ('Анна', 'Петрова', '2004-03-22', 'Ж', 1, 2, 'active'),
            ('Дмитрий', 'Сидоров', '2006-07-10', 'М', 1, 1, 'active'),
        ]
        
        for first_name, last_name, birth_date, gender, sport_id, region_id, status in athletes:
            cursor.execute(
                """INSERT INTO athletes 
                   (first_name, last_name, birth_date, gender, sport_id, region_id, program_status) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;""",
                (first_name, last_name, birth_date, gender, sport_id, region_id, status)
            )
        
        conn.commit()
        print("\n✅ Тестовые данные добавлены успешно!\n")
        
        print("🔐 Тестовые учетные данные:")
        print("  - admin / admin123 (администратор)")
        print("  - curator_ski / curator123 (куратор)")
        print("  - ivanov_a / athlete123 (спортсмен)\n")
        
        return True
    
    except Exception as e:
        print(f"⚠️  Ошибка при добавлении тестовых данных: {e}")
        print("  (Таблицы созданы, но тестовые данные не добавлены)\n")
        return False

def main():
    """Главная функция"""
    print("\n" + "="*60)
    print("🚀 ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ SUPABASE")
    print("="*60 + "\n")
    
    print("⚠️  ВАЖНО: Перед запуском убедись что:")
    print("  1. Пароль Supabase вставлен в переменную DB_CONFIG")
    print("  2. Подключение к интернету работает")
    print("  3. Supabase проект создан\n")
    
    input("Нажми Enter для продолжения...")
    
    success = create_tables()
    
    if success:
        print("="*60)
        print("✅ УСПЕШНО! База данных инициализирована!")
        print("="*60)
        print("\n📊 Таблицы созданы:")
        print("  - sports (виды спорта)")
        print("  - regions (регионы)")
        print("  - users (пользователи)")
        print("  - athletes (спортсмены)")
        print("  - sport_results (результаты соревнований)")
        print("  - functional_tests (функциональные тесты)")
        print("  - medical_data (медицинские данные)")
        print("  - development_plans (планы развития)")
        print("  - documents (документы)")
        print("\n🔐 Тестовые пользователи созданы!")
        print("   Запусти приложение: streamlit run app.py\n")
    else:
        print("="*60)
        print("❌ ОШИБКА! Проверь параметры подключения.")
        print("="*60 + "\n")

if __name__ == '__main__':
    main()
