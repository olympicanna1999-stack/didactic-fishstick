"""
Главный файл веб-приложения "Цифровой реестр олимпийского резерва"
Streamlit Application - исправленная версия для Streamlit Cloud
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path
import os

# Добавляем путь к utils
sys.path.insert(0, str(Path(__file__).parent.absolute()))

# Импорт модулей с обработкой ошибок
try:
    from utils.auth import check_authentication, get_current_user, logout_user
    from utils.database import get_db_connection, init_database
except ImportError as e:
    st.error(f"""
    ❌ Ошибка импорта модулей: {e}
    
    **Решение:**
    Убедитесь, что в GitHub репозитории созданы папки и файлы:
    - utils/__init__.py
    - utils/auth.py
    - utils/database.py
    - utils/charts.py
    
    Читайте файл QUICK-FIX.md
    """)
    st.stop()

# Конфигурация страницы
st.set_page_config(
    page_title="Цифровой реестр олимпийского резерва",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кастомный CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .stat-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #666;
    }
    .info-box {
        background-color: #e7f3ff;
        padding: 1rem;
        border-left: 4px solid #1f77b4;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Главная функция приложения"""
    
    # Проверка аутентификации
    if not check_authentication():
        show_login_page()
        return
    
    # Получение текущего пользователя
    user = get_current_user()
    
    # Боковая панель
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Olympic_rings_without_rims.svg/1200px-Olympic_rings_without_rims.svg.png", width=150)
        st.title("🏅 Олимпийский резерв")
        st.divider()
        
        # Информация о пользователе
        st.write(f"**Пользователь:** {user['username']}")
        st.write(f"**Роль:** {get_role_name(user['role'])}")
        
        if user['role'] == 'curator' and user.get('sport_name'):
            st.write(f"**Вид спорта:** {user['sport_name']}")
        
        st.divider()
        
        # Навигация
        st.subheader("📋 Навигация")
        st.page_link("app.py", label="🏠 Главная", icon="🏠")
        
        if user['role'] in ['admin', 'curator']:
            st.page_link("pages/1_База_спортсменов.py", label="👥 База спортсменов", icon="👥")
        
        st.page_link("pages/2_Профиль_спортсмена.py", label="📊 Профиль спортсмена", icon="📊")
        
        if user['role'] in ['admin', 'curator']:
            st.page_link("pages/3_Аналитика.py", label="📈 Аналитика", icon="📈")
        
        if user['role'] == 'admin':
            st.page_link("pages/4_Управление.py", label="⚙️ Управление", icon="⚙️")
        
        st.divider()
        
        if st.button("🚪 Выход", use_container_width=True):
            logout_user()
            st.rerun()
    
    # Основной контент
    show_main_page(user)

def show_login_page():
    """Отображение страницы входа"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<h1 class="main-header">🏅 Цифровой реестр<br>олимпийского резерва</h1>', unsafe_allow_html=True)
        
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("""
        **Добро пожаловать!**
        
        Защищенный веб-портал для управления данными олимпийского резерва России.
        Система обеспечивает хранение и мониторинг информации о спортсменах,
        их результатах, медицинских показателях и планах развития.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("🔐 Вход в систему")
        
        with st.form("login_form"):
            username = st.text_input("Логин", placeholder="Введите логин")
            password = st.text_input("Пароль", type="password", placeholder="Введите пароль")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit = st.form_submit_button("Войти", use_container_width=True, type="primary")
            with col_btn2:
                st.form_submit_button("Забыли пароль?", use_container_width=True)
            
            if submit:
                if username and password:
                    from utils.auth import authenticate_user
                    if authenticate_user(username, password):
                        st.success("✅ Вход выполнен успешно!")
                        st.rerun()
                    else:
                        st.error("❌ Неверный логин или пароль")
                else:
                    st.warning("⚠️ Заполните все поля")
        
        st.divider()
        
        with st.expander("ℹ️ Тестовые учетные данные"):
            st.markdown("""
            **Администратор ОКР:**
            - Логин: `admin`
            - Пароль: `admin123`
            
            **Куратор (Лыжные гонки):**
            - Логин: `curator_ski`
            - Пароль: `curator123`
            
            **Спортсмен:**
            - Логин: `ivanov_a`
            - Пароль: `athlete123`
            """)

def show_main_page(user):
    """Отображение главной страницы"""
    
    st.markdown('<h1 class="main-header">🏠 Главная панель</h1>', unsafe_allow_html=True)
    
    # Приветствие
    st.markdown(f"""
    ### Добро пожаловать, {user['username']}!
    
    Сегодня: **{datetime.now().strftime('%d.%m.%Y')}**
    """)
    
    # Статистика в зависимости от роли
    show_statistics(user)
    
    st.divider()
    
    # Последние обновления
    show_recent_updates(user)

def show_statistics(user):
    """Отображение статистики"""
    
    try:
        conn = get_db_connection()
        
        if user['role'] == 'admin':
            # Статистика для администратора
            st.subheader("📊 Общая статистика системы")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                try:
                    total_athletes = pd.read_sql(
                        "SELECT COUNT(*) as count FROM athletes WHERE program_status='active'",
                        conn
                    )
                    count = total_athletes['count'][0] if not total_athletes.empty else 0
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-number">{count}</div>
                        <div class="stat-label">Активных спортсменов</div>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"⚠️ Ошибка загрузки: {str(e)[:50]}")
            
            with col2:
                try:
                    total_sports = pd.read_sql(
                        "SELECT COUNT(DISTINCT sport_id) as count FROM athletes",
                        conn
                    )
                    count = total_sports['count'][0] if not total_sports.empty else 0
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-number">{count}</div>
                        <div class="stat-label">Видов спорта</div>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"⚠️ Ошибка загрузки: {str(e)[:50]}")
            
            with col3:
                try:
                    total_results = pd.read_sql(
                        "SELECT COUNT(*) as count FROM sport_results WHERE competition_date >= CURRENT_DATE - INTERVAL '30 days'",
                        conn
                    )
                    count = total_results['count'][0] if not total_results.empty else 0
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-number">{count}</div>
                        <div class="stat-label">Результатов за месяц</div>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"⚠️ Ошибка загрузки: {str(e)[:50]}")
            
            with col4:
                try:
                    total_regions = pd.read_sql(
                        "SELECT COUNT(DISTINCT region_id) as count FROM athletes",
                        conn
                    )
                    count = total_regions['count'][0] if not total_regions.empty else 0
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-number">{count}</div>
                        <div class="stat-label">Регионов представлено</div>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"⚠️ Ошибка загрузки: {str(e)[:50]}")
        
        elif user['role'] == 'curator':
            # Статистика для куратора
            st.subheader(f"📊 Статистика: {user.get('sport_name', 'Ваш вид спорта')}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                try:
                    query = f"SELECT COUNT(*) as count FROM athletes WHERE sport_id={user.get('sport_id')} AND program_status='active'"
                    athletes_count = pd.read_sql(query, conn)
                    count = athletes_count['count'][0] if not athletes_count.empty else 0
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-number">{count}</div>
                        <div class="stat-label">Ваших спортсменов</div>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"⚠️ Ошибка: {str(e)[:50]}")
            
            with col2:
                try:
                    query = f"""
                    SELECT COUNT(*) as count FROM sport_results sr
                    JOIN athletes a ON sr.athlete_id = a.id
                    WHERE a.sport_id={user.get('sport_id')} 
                    AND sr.competition_date >= CURRENT_DATE - INTERVAL '30 days'
                    """
                    recent_results = pd.read_sql(query, conn)
                    count = recent_results['count'][0] if not recent_results.empty else 0
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-number">{count}</div>
                        <div class="stat-label">Результатов за месяц</div>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"⚠️ Ошибка: {str(e)[:50]}")
            
            with col3:
                try:
                    query = f"""
                    SELECT COUNT(*) as count FROM development_plans dp
                    JOIN athletes a ON dp.athlete_id = a.id
                    WHERE a.sport_id={user.get('sport_id')} AND dp.status='active'
                    """
                    active_plans = pd.read_sql(query, conn)
                    count = active_plans['count'][0] if not active_plans.empty else 0
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-number">{count}</div>
                        <div class="stat-label">Активных планов</div>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"⚠️ Ошибка: {str(e)[:50]}")
        
        elif user['role'] == 'athlete':
            # Статистика для спортсмена
            st.subheader("📊 Ваша статистика")
            
            athlete_id = user.get('athlete_id')
            if athlete_id:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    try:
                        query = f"SELECT COUNT(*) as count FROM sport_results WHERE athlete_id={athlete_id}"
                        total_comps = pd.read_sql(query, conn)
                        count = total_comps['count'][0] if not total_comps.empty else 0
                        st.markdown(f"""
                        <div class="stat-card">
                            <div class="stat-number">{count}</div>
                            <div class="stat-label">Соревнований</div>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.warning(f"⚠️ Ошибка: {str(e)[:50]}")
                
                with col2:
                    try:
                        query = f"SELECT COUNT(*) as count FROM sport_results WHERE athlete_id={athlete_id} AND is_personal_best=TRUE"
                        personal_bests = pd.read_sql(query, conn)
                        count = personal_bests['count'][0] if not personal_bests.empty else 0
                        st.markdown(f"""
                        <div class="stat-card">
                            <div class="stat-number">{count}</div>
                            <div class="stat-label">Личных рекордов</div>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.warning(f"⚠️ Ошибка: {str(e)[:50]}")
                
                with col3:
                    try:
                        query = f"SELECT COUNT(*) as count FROM functional_tests WHERE athlete_id={athlete_id}"
                        total_tests = pd.read_sql(query, conn)
                        count = total_tests['count'][0] if not total_tests.empty else 0
                        st.markdown(f"""
                        <div class="stat-card">
                            <div class="stat-number">{count}</div>
                            <div class="stat-label">Тестирований</div>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.warning(f"⚠️ Ошибка: {str(e)[:50]}")
        
        conn.close()
    
    except Exception as e:
        st.warning(f"⚠️ Не удалось загрузить статистику: {e}")

def show_recent_updates(user):
    """Отображение последних обновлений"""
    
    st.subheader("🔔 Последние обновления")
    
    try:
        conn = get_db_connection()
        
        if user['role'] == 'admin':
            # Последние результаты всех спортсменов
            query = """
            SELECT 
                a.last_name || ' ' || a.first_name as athlete_name,
                s.name as sport_name,
                sr.competition_name,
                sr.discipline,
                sr.result,
                sr.place,
                sr.competition_date
            FROM sport_results sr
            JOIN athletes a ON sr.athlete_id = a.id
            JOIN sports s ON a.sport_id = s.id
            ORDER BY sr.competition_date DESC
            LIMIT 10
            """
            recent = pd.read_sql(query, conn)
            
            if not recent.empty:
                recent['competition_date'] = pd.to_datetime(recent['competition_date']).dt.strftime('%d.%m.%Y')
                st.dataframe(recent, use_container_width=True, hide_index=True)
            else:
                st.info("Нет данных для отображения")
        
        elif user['role'] == 'curator':
            # Последние результаты спортсменов куратора
            query = f"""
            SELECT 
                a.last_name || ' ' || a.first_name as athlete_name,
                sr.competition_name,
                sr.discipline,
                sr.result,
                sr.place,
                sr.competition_date
            FROM sport_results sr
            JOIN athletes a ON sr.athlete_id = a.id
            WHERE a.sport_id = {user.get('sport_id')}
            ORDER BY sr.competition_date DESC
            LIMIT 10
            """
            recent = pd.read_sql(query, conn)
            
            if not recent.empty:
                recent['competition_date'] = pd.to_datetime(recent['competition_date']).dt.strftime('%d.%m.%Y')
                st.dataframe(recent, use_container_width=True, hide_index=True)
            else:
                st.info("Нет данных для отображения")
        
        elif user['role'] == 'athlete':
            # Последние результаты спортсмена
            athlete_id = user.get('athlete_id')
            if athlete_id:
                query = f"""
                SELECT 
                    competition_name,
                    discipline,
                    result,
                    place,
                    competition_date,
                    is_personal_best
                FROM sport_results
                WHERE athlete_id = {athlete_id}
                ORDER BY competition_date DESC
                LIMIT 10
                """
                recent = pd.read_sql(query, conn)
                
                if not recent.empty:
                    recent['competition_date'] = pd.to_datetime(recent['competition_date']).dt.strftime('%d.%m.%Y')
                    recent['is_personal_best'] = recent['is_personal_best'].map({True: '🏆 ЛР', False: ''})
                    st.dataframe(recent, use_container_width=True, hide_index=True)
                else:
                    st.info("Нет данных для отображения")
        
        conn.close()
    
    except Exception as e:
        st.warning(f"⚠️ Ошибка загрузки обновлений: {e}")

def get_role_name(role):
    """Получение русского названия роли"""
    roles = {
        'admin': 'Администратор ОКР',
        'curator': 'Куратор по виду спорта',
        'athlete': 'Спортсмен'
    }
    return roles.get(role, role)

if __name__ == "__main__":
    # Инициализация базы данных при первом запуске
    try:
        init_database()
    except Exception as e:
        pass  # Ошибка инициализации БД не должна прерывать приложение
    
    main()
