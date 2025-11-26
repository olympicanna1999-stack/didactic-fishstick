 Returns:
        Подключение к БД (psycopg2 connection object)
    """
    try:
        # Используем параметры из переменной выше
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['username'],
            password=DB_CONFIG['password'],
            connect_timeout=10
        )
        return conn
    
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        
        st.error(f"""
        ❌ **Ошибка подключения к БД!**
        
        **Детали:** {error_msg[:200]}
        
        **Что проверить:**
        
        1. ✅ **В файле utils/database.py найди DB_CONFIG:**
           ```python
           DB_CONFIG = {{
               'host': 'db.bssbrxzbljzanponotmc.supabase.co',
               'port': 5432,
               'database': 'postgres',
               'username': 'postgres',
               'password': 'Rqyd6a6luT0k35oG',  # ← ЗАМЕНИ!
           }}
           ```
        
        2. ✅ **Вставь пароль из Supabase:**
           - https://supabase.com/dashboard
           - Settings → Database → Connection string
           - Скопируй пароль (между `:` и `@`)
        
        3. ✅ **Проверь параметры:**
           - host: `db.bssbrxzbljzanponotmc.supabase.co` ✓
           - database: `postgres` ✓
           - username: `postgres` ✓
           - password: твой реальный пароль ✓
        
        4. ✅ **Перезагрузи приложение:**
           - На Streamlit Cloud: ⚙️ Settings → Reboot app
        """)
        st.stop()
    
    except Exception as e:
        st.error(f"""
        ❌ **Неожиданная ошибка: {e}**
        
        Пожалуйста, проверьте параметры в DB_CONFIG
        """)
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
    """Получение списка спортсменов"""
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
    """Получение спортсмена по ID"""
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
    """Получение спортивных результатов"""
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
    """Добавление нового спортивного результата"""
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
    """Получение функциональных тестов спортсмена"""
    query = f"""
    SELECT * FROM functional_tests
    WHERE athlete_id = %s
    ORDER BY test_date DESC
    LIMIT {limit}
    """
    return execute_query(query, [athlete_id])

# ==================== ФУНКЦИИ ДЛЯ МЕДИЦИНСКИХ ДАННЫХ ====================

def get_medical_data(athlete_id: int, limit=50):
    """Получение медицинских данных спортсмена"""
    query = f"""
    SELECT * FROM medical_data
    WHERE athlete_id = %s
    ORDER BY examination_date DESC
    LIMIT {limit}
    """
    return execute_query(query, [athlete_id])

# ==================== ФУНКЦИИ ДЛЯ СПРАВОЧНИКОВ ====================

def get_sports():
    """Получение списка видов спорта"""
    query = "SELECT * FROM sports ORDER BY name"
    return execute_query(query)

def get_regions():
    """Получение списка регионов"""
    query = "SELECT * FROM regions ORDER BY name"
    return execute_query(query)

def get_development_plans(athlete_id: int):
    """Получение планов развития спортсмена"""
    query = """
    SELECT * FROM development_plans
    WHERE athlete_id = %s
    ORDER BY plan_date DESC
    """
    return execute_query(query, [athlete_id])

def get_documents(athlete_id: int):
    """Получение документов спортсмена"""
    query = """
    SELECT * FROM documents
    WHERE athlete_id = %s
    ORDER BY created_at DESC
    """
    return execute_query(query, [athlete_id])

# ==================== ФУНКЦИИ ДЛЯ СТАТИСТИКИ ====================

def get_athlete_statistics(athlete_id: int):
    """Получение статистики спортсмена"""
    stats = {}
    
    comps = execute_query("SELECT COUNT(*) as count FROM sport_results WHERE athlete_id = %s", [athlete_id])
    stats['total_competitions'] = comps['count'][0] if not comps.empty else 0
    
    pbs = execute_query("SELECT COUNT(*) as count FROM sport_results WHERE athlete_id = %s AND is_personal_best = TRUE", [athlete_id])
    stats['personal_bests'] = pbs['count'][0] if not pbs.empty else 0
    
    places = execute_query("SELECT AVG(place) as avg_place FROM sport_results WHERE athlete_id = %s", [athlete_id])
    stats['avg_place'] = round(places['avg_place'][0], 2) if not places.empty and places['avg_place'][0] else None
    
    return stats

def get_sport_statistics(sport_id: int):
    """Получение статистики по виду спорта"""
    stats = {}
    
    athletes_count = execute_query(
        "SELECT COUNT(*) as count FROM athletes WHERE sport_id = %s AND program_status = 'active'",
        [sport_id]
    )
    stats['total_athletes'] = athletes_count['count'][0] if not athletes_count.empty else 0
    
    results_count = execute_query(
        """SELECT COUNT(*) as count FROM sport_results sr
           JOIN athletes a ON sr.athlete_id = a.id
           WHERE a.sport_id = %s""",
        [sport_id]
    )
    stats['total_results'] = results_count['count'][0] if not results_count.empty else 0
    
    return stats
