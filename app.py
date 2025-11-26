"""
Олимпийский резерв - Расширенная версия с видами спорта и тренерами
Цифровой реестр олимпийского резерва
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from pathlib import Path
from datetime import datetime, timedelta

from utils.database import (
    init_database, get_athletes, get_athlete_by_id, get_sport_results,
    get_total_athletes, get_total_competitions,
    get_user_by_username, add_athlete, add_sport_result, execute_query
)

# ==================== КОНФИГУРАЦИЯ ====================

st.set_page_config(
    page_title="🏅 Олимпийский резерв",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Профессиональная цветовая схема
custom_theme = """
<style>
    :root {
        --primary: #667eea;
        --secondary: #764ba2;
        --accent: #f093fb;
    }
    
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    h1 {
        color: #1f2937;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
    }
    
    .metric-container {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        transition: transform 0.2s;
    }
</style>
"""

st.markdown(custom_theme, unsafe_allow_html=True)

sns.set_theme(style="whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 6)

# ==================== ВИДЫ СПОРТА И РЕГИОНЫ ====================

SPORTS_LIST = {
    "Лыжные гонки": "🎿",
    "Гребля": "🚣",
    "Биатлон": "🎯"
}

REGIONS = [
    "Республика Карелия",
    "Архангельская область",
    "Мурманская область",
    "Ненецкий АО",
    "Вологодская область",
    "Тверская область",
    "Костромская область",
    "Кировская область",
    "Удмуртия",
    "Республика Татарстан"
]

COACHES = {
    "Лыжные гонки": [
        "Иван Петров", "Сергей Смирнов", "Дмитрий Морозов",
        "Алексей Волков", "Николай Соколов"
    ],
    "Гребля": [
        "Владимир Кузнецов", "Олег Лебедев", "Борис Орлов",
        "Виктор Комаров", "Игорь Новиков"
    ],
    "Биатлон": [
        "Анатолий Зайцев", "Павел Ивановский", "Юрий Константинов",
        "Геннадий Лаврентьев", "Валентин Макаров"
    ]
}

# ==================== МОК-ДАННЫЕ С РАСШИРЕННОЙ ИНФОРМАЦИЕЙ ====================

def add_extended_mock_data():
    """Добавляет расширенные мок-данные с видами спорта и тренерами"""
    
    athletes_count = execute_query("SELECT COUNT(*) as count FROM athletes").iloc[0]['count']
    
    if athletes_count <= 3:
        # Спортсмены по видам спорта
        athletes_by_sport = {
            "Лыжные гонки": [
                ("Александр", "Смирнов", "2003-02-14", "М"),
                ("Сергей", "Петров", "2004-08-10", "М"),
                ("Дмитрий", "Морозов", "2005-03-18", "М"),
                ("Мария", "Волкова", "2004-05-20", "Ж"),
                ("Екатерина", "Соколова", "2004-11-25", "Ж"),
                ("Анастасия", "Леонова", "2005-06-30", "Ж"),
            ],
            "Гребля": [
                ("Никита", "Орлов", "2003-09-12", "М"),
                ("Максим", "Зайцев", "2005-01-22", "М"),
                ("Андрей", "Ивановский", "2004-06-15", "М"),
                ("Валерия", "Лебедева", "2004-12-08", "Ж"),
                ("Дарья", "Новикова", "2006-04-15", "Ж"),
                ("Ольга", "Соколова", "2005-02-28", "Ж"),
            ],
            "Биатлон": [
                ("Павел", "Федоров", "2005-04-10", "М"),
                ("Елена", "Кузнецова", "2004-07-10", "Ж"),
            ]
        }
        
        import random
        np.random.seed(42)
        random.seed(42)
        
        # Добавляем спортсменов с дополнительной информацией
        athlete_data_store = {}
        
        for sport, athletes in athletes_by_sport.items():
            for first_name, last_name, birth_date, gender in athletes:
                region = random.choice(REGIONS)
                coach = random.choice(COACHES[sport])
                
                # Добавляем спортсмена
                athlete_id = add_athlete(first_name, last_name, birth_date, gender, 'active')
                
                # Сохраняем данные
                athlete_data_store[athlete_id] = {
                    'sport': sport,
                    'region': region,
                    'coach': coach,
                    'first_name': first_name,
                    'last_name': last_name
                }
                
                # Генерируем результаты
                competitions = {
                    "Лыжные гонки": [
                        'Чемпионат России',
                        'Кубок России',
                        'Чемпионат Европы юниоров',
                        'Чемпионат мира юниоров',
                        'Спартакиада регионов',
                    ],
                    "Гребля": [
                        'Чемпионат России',
                        'Кубок России',
                        'Чемпионат Европы юниоров',
                        'Чемпионат мира юниоров',
                        'Открытый чемпионат города',
                    ],
                    "Биатлон": [
                        'Чемпионат России',
                        'Кубок России',
                        'Чемпионат Европы юниоров',
                        'Этап Кубка мира',
                        'Спартакиада регионов',
                    ]
                }
                
                disciplines = {
                    "Лыжные гонки": ['Спринт 1км', 'Классический стиль 5км', 'Свободный стиль 5км', 'Длинная дистанция 10км'],
                    "Гребля": ['Одиночка 2км', 'Двойка 2км', 'Четвёрка 2км', 'Командная эстафета'],
                    "Биатлон": ['Спринт 7.5км', 'Гонка преследования', 'Индивидуальная 15км', 'Эстафета']
                }
                
                for _ in range(15):
                    comp_date = datetime.now() - timedelta(days=random.randint(1, 365))
                    comp_name = random.choice(competitions[sport])
                    discipline = random.choice(disciplines[sport])
                    
                    if sport == "Лыжные гонки":
                        time_sec = random.randint(180, 600)
                    elif sport == "Гребля":
                        time_sec = random.randint(240, 420)
                    else:  # Биатлон
                        time_sec = random.randint(900, 1800)
                    
                    minutes = time_sec // 60
                    seconds = time_sec % 60
                    result_time = f"{minutes}:{seconds:02d}"
                    place = random.randint(1, 12)
                    
                    add_sport_result(athlete_id, comp_name, comp_date.strftime('%Y-%m-%d'), 
                                   discipline, result_time, place)

# ==================== ПОЛУЧЕНИЕ ДАННЫХ СПОРТСМЕНОВ ====================

def get_athletes_with_details():
    """Получает спортсменов с деталями (спорт, регион, тренер)"""
    athletes = get_athletes()
    
    if athletes.empty:
        return athletes
    
    # Генерируем детали для каждого спортсмена
    details = []
    import random
    
    for idx, row in athletes.iterrows():
        sport = random.choice(list(SPORTS_LIST.keys()))
        region = random.choice(REGIONS)
        coach = random.choice(COACHES[sport])
        
        details.append({
            'id': row['id'],
            'first_name': row['first_name'],
            'last_name': row['last_name'],
            'gender': row['gender'],
            'program_status': row['program_status'],
            'birth_date': row['birth_date'],
            'sport': sport,
            'region': region,
            'coach': coach
        })
    
    return pd.DataFrame(details)

# ==================== ИНИЦИАЛИЗАЦИЯ ====================

if 'db_initialized' not in st.session_state:
    init_database()
    add_extended_mock_data()
    st.session_state.db_initialized = True

# ==================== ГЛАВНАЯ СТРАНИЦА ====================

def main():
    """Главная функция приложения"""
    
    if 'user' not in st.session_state:
        show_login_page()
        return
    
    show_main_dashboard()

def show_login_page():
    """Форма входа"""
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 40px 0;'>
            <h1 style='font-size: 3rem; margin: 0;'>🏅</h1>
            <h1>Олимпийский резерв</h1>
            <p style='font-size: 1.1rem; color: #666;'>Цифровой реестр спортсменов</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        username = st.text_input("👤 Логин", placeholder="Введите логин", key="login")
        password = st.text_input("🔑 Пароль", type="password", placeholder="Введите пароль", key="password")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("✅ Войти", use_container_width=True, type="primary"):
                if authenticate_user(username, password):
                    st.success("✅ Вход выполнен успешно!")
                    st.rerun()
                else:
                    st.error("❌ Неправильный логин или пароль")
        
        st.markdown("---")
        with st.expander("📋 Тестовые учетные данные"):
            st.markdown("""
            - **admin** / admin123
            - **curator_ski** / curator123
            - **ivanov_a** / athlete123
            """)

def show_main_dashboard():
    """Главная панель"""
    
    user = st.session_state.get('user', {})
    username = user.get('username', 'Unknown')
    
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 20px 0; margin-bottom: 20px;'>
            <h2 style='margin: 0;'>🏅 Олимпийский резерв</h2>
            <p style='margin: 10px 0 0 0; color: #666;'>v2.1.0</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**👤 {username}**")
        st.markdown("---")
        
        page = st.radio(
            "📊 Навигация:",
            ["🏠 Главная", "👥 База спортсменов", "📈 Аналитика", "🏆 Результаты", "⚙️ Настройки"],
            index=0
        )
        
        st.markdown("---")
        
        if st.button("🚪 Выход", use_container_width=True):
            if 'user' in st.session_state:
                del st.session_state['user']
            st.rerun()
    
    if page == "🏠 Главная":
        show_home_page()
    elif page == "👥 База спортсменов":
        show_athletes_page()
    elif page == "📈 Аналитика":
        show_analytics_page()
    elif page == "🏆 Результаты":
        show_results_page()
    elif page == "⚙️ Настройки":
        show_settings_page()

def show_home_page():
    """Главная страница"""
    st.title("🏠 Главная панель")
    
    total_athletes = get_total_athletes()
    total_competitions = get_total_competitions()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Спортсменов", total_athletes, "+3", help="Всего активных спортсменов")
    with col2:
        st.metric("🏆 Соревнований", total_competitions, "+15", help="Всего проведено соревнований")
    with col3:
        st.metric("🎿 Виды спорта", "3", help="Лыжные гонки, Гребля, Биатлон")
    with col4:
        st.metric("🗺️ Регионов", len(REGIONS), help="Регионы России")
    
    st.markdown("---")
    
    # Распределение по видам спорта
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Распределение по видам спорта")
        athletes = get_athletes()
        
        if not athletes.empty:
            sports_data = []
            for sport in SPORTS_LIST.keys():
                # Примерное распределение
                if sport == "Лыжные гонки":
                    count = 6
                elif sport == "Гребля":
                    count = 6
                else:
                    count = 2
                sports_data.append({'Вид спорта': sport, 'Количество': count})
            
            sports_df = pd.DataFrame(sports_data)
            fig, ax = plt.subplots(figsize=(8, 6))
            colors = ['#667eea', '#764ba2', '#f093fb']
            wedges, texts, autotexts = ax.pie(
                sports_df['Количество'],
                labels=sports_df['Вид спорта'],
                autopct='%1.1f%%',
                colors=colors,
                startangle=90
            )
            ax.set_title("Распределение спортсменов", fontsize=12, fontweight='bold')
            st.pyplot(fig)
    
    with col2:
        st.subheader("🏢 Распределение по регионам")
        regions_data = []
        
        import random
        np.random.seed(42)
        for region in REGIONS[:5]:
            regions_data.append({'Регион': region, 'Спортсмены': random.randint(1, 3)})
        
        regions_df = pd.DataFrame(regions_data)
        fig, ax = plt.subplots(figsize=(8, 6))
        bars = ax.barh(regions_df['Регион'], regions_df['Спортсмены'], color='#667eea')
        ax.set_xlabel("Количество спортсменов", fontsize=11, fontweight='bold')
        ax.set_title("Топ регионов", fontsize=12, fontweight='bold')
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{int(width)}', ha='left', va='center', fontweight='bold')
        st.pyplot(fig)

def show_athletes_page():
    """Страница со спортсменами с фильтрами по видам спорта"""
    st.title("👥 База спортсменов")
    
    if st.session_state.get('show_athlete_profile', False) and 'selected_athlete_id' in st.session_state:
        show_athlete_profile_page(st.session_state['selected_athlete_id'])
        
        if st.button("← Вернуться к списку"):
            st.session_state['show_athlete_profile'] = False
            st.rerun()
        return
    
    tab1, tab2 = st.tabs(["📋 Список", "➕ Добавить"])
    
    with tab1:
        st.subheader("Все спортсмены")
        
        athletes = get_athletes()
        if not athletes.empty:
            # Фильтры
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                sport_filter = st.multiselect(
                    "Вид спорта:",
                    list(SPORTS_LIST.keys()),
                    default=list(SPORTS_LIST.keys())
                )
            
            with col2:
                gender_filter = st.multiselect(
                    "Пол:",
                    athletes['gender'].unique(),
                    default=athletes['gender'].unique()
                )
            
            with col3:
                status_filter = st.multiselect(
                    "Статус:",
                    athletes['program_status'].unique(),
                    default=athletes['program_status'].unique()
                )
            
            with col4:
                region_filter = st.multiselect(
                    "Регионы:",
                    REGIONS,
                    default=REGIONS[:5]
                )
            
            st.markdown("---")
            
            # Применяем фильтры (примерная логика)
            filtered = athletes[
                (athletes['gender'].isin(gender_filter)) & 
                (athletes['program_status'].isin(status_filter))
            ]
            
            st.markdown(f"### Найдено спортсменов: {len(filtered)}")
            
            # Таблица с дополнительной информацией
            display_data = []
            import random
            np.random.seed(42)
            
            for idx, row in filtered.iterrows():
                sport = random.choice(sport_filter)
                region = random.choice(region_filter)
                coach = random.choice(COACHES[sport])
                
                display_data.append({
                    'ID': int(row['id']),
                    'Имя': row['first_name'],
                    'Фамилия': row['last_name'],
                    '🏅 Вид спорта': f"{SPORTS_LIST[sport]} {sport}",
                    '👨‍🏫 Тренер': coach,
                    '🗺️ Регион': region,
                    'Пол': '👨' if row['gender'] == 'М' else '👩',
                    'Статус': '✅ Активен' if row['program_status'] == 'active' else '⏸ Неактивен'
                })
            
            if display_data:
                df_display = pd.DataFrame(display_data)
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.markdown("### 👤 Нажмите на ID спортсмена для просмотра профиля:")
                
                for data in display_data:
                    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
                    
                    with col1:
                        st.text(f"ID: {data['ID']}")
                    with col2:
                        st.text(f"{data['Имя']} {data['Фамилия']}")
                    with col3:
                        st.text(data['🏅 Вид спорта'])
                    with col4:
                        st.text(f"👨‍🏫 {data['👨‍🏫 Тренер']}")
                    with col5:
                        if st.button("📋", key=f"athlete_btn_{data['ID']}", help="Профиль"):
                            st.session_state['selected_athlete_id'] = data['ID']
                            st.session_state['show_athlete_profile'] = True
                            st.rerun()
            else:
                st.info("📭 Нет спортсменов по выбранным фильтрам")
        else:
            st.info("📭 Нет спортсменов")
    
    with tab2:
        st.subheader("Добавить нового спортсмена")
        
        with st.form("add_athlete_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("Имя:")
                last_name = st.text_input("Фамилия:")
                birth_date = st.date_input("Дата рождения:")
            
            with col2:
                gender = st.selectbox("Пол:", ["М", "Ж"])
                sport = st.selectbox("Вид спорта:", list(SPORTS_LIST.keys()))
                region = st.selectbox("Регион:", REGIONS)
            
            coach = st.selectbox("Тренер:", COACHES[sport])
            
            if st.form_submit_button("✅ Добавить", type="primary"):
                if add_athlete(first_name, last_name, str(birth_date), gender, 'active'):
                    st.success("✅ Спортсмен добавлен!")
                    st.rerun()
                else:
                    st.error("❌ Ошибка при добавлении")

def show_athlete_profile_page(athlete_id: int):
    """Показывает профиль спортсмена"""
    try:
        pages_path = Path(__file__).parent / 'pages'
        if str(pages_path) not in sys.path:
            sys.path.insert(0, str(pages_path))
        
        from athlete_profile import show_athlete_profile
        show_athlete_profile(athlete_id)
    except Exception as e:
        st.error(f"❌ Ошибка загрузки профиля: {e}")

def show_analytics_page():
    """Страница аналитики"""
    st.title("📈 Аналитика и Дашборды")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 По видам спорта", "🗺️ По регионам", "👨‍🏫 Тренеры", "🏆 Результаты"])
    
    with tab1:
        st.subheader("Анализ по видам спорта")
        
        col1, col2 = st.columns(2)
        
        with col1:
            sports_stats = {
                "🎿 Лыжные гонки": {"Спортсмены": 6, "Результаты": 90, "Тренеры": 5},
                "🚣 Гребля": {"Спортсмены": 6, "Результаты": 90, "Тренеры": 5},
                "🎯 Биатлон": {"Спортсмены": 2, "Результаты": 30, "Тренеры": 5}
            }
            
            for sport, data in sports_stats.items():
                with st.container():
                    st.markdown(f"### {sport}")
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("Спортсмены", data["Спортсмены"])
                    col_b.metric("Результаты", data["Результаты"])
                    col_c.metric("Тренеры", data["Тренеры"])
                st.divider()
        
        with col2:
            fig, ax = plt.subplots(figsize=(8, 6))
            sports = ["🎿 Лыжные гонки", "🚣 Гребля", "🎯 Биатлон"]
            athletes = [6, 6, 2]
            colors = ['#667eea', '#764ba2', '#f093fb']
            bars = ax.bar(sports, athletes, color=colors, edgecolor='black', linewidth=1.5)
            ax.set_ylabel("Количество спортсменов", fontsize=11, fontweight='bold')
            ax.set_title("Распределение по видам спорта", fontsize=12, fontweight='bold')
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom', fontweight='bold')
            plt.xticks(rotation=15)
            st.pyplot(fig)
    
    with tab2:
        st.subheader("Географическое распределение")
        
        regions_count = {}
        import random
        np.random.seed(42)
        for region in REGIONS[:8]:
            regions_count[region] = random.randint(1, 3)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        regions = list(regions_count.keys())
        counts = list(regions_count.values())
        bars = ax.barh(regions, counts, color='#667eea', edgecolor='black', linewidth=1.5)
        ax.set_xlabel("Количество спортсменов", fontsize=11, fontweight='bold')
        ax.set_title("Распределение по регионам", fontsize=12, fontweight='bold')
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{int(width)}', ha='left', va='center', fontweight='bold')
        st.pyplot(fig)
    
    with tab3:
        st.subheader("Тренеры и их команды")
        
        col1, col2, col3 = st.columns(3)
        
        for col, (sport, coaches) in zip([col1, col2, col3], COACHES.items()):
            with col:
                st.markdown(f"### {SPORTS_LIST[sport]} {sport}")
                for coach in coaches:
                    st.markdown(f"- **{coach}**")
    
    with tab4:
        st.subheader("Статистика результатов")
        
        results = get_sport_results(limit=100)
        if not results.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                athlete_results = results.groupby('athlete_id').size().head(10)
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.barh(range(len(athlete_results)), athlete_results.values, color='#667eea')
                ax.set_yticks(range(len(athlete_results)))
                ax.set_yticklabels([f'Спортсмен {aid}' for aid in athlete_results.index])
                ax.set_xlabel("Количество результатов", fontsize=11, fontweight='bold')
                ax.set_title("Активность спортсменов", fontsize=12, fontweight='bold')
                st.pyplot(fig)
            
            with col2:
                if 'place' in results.columns:
                    place_counts = results['place'].value_counts().sort_index().head(10)
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.plot(place_counts.index, place_counts.values, marker='o', linewidth=2.5,
                           markersize=10, color='#667eea', markerfacecolor='#f093fb', markeredgewidth=2)
                    ax.fill_between(place_counts.index, place_counts.values, alpha=0.2, color='#667eea')
                    ax.set_xlabel("Место", fontsize=11, fontweight='bold')
                    ax.set_ylabel("Количество", fontsize=11, fontweight='bold')
                    ax.set_title("Распределение мест", fontsize=12, fontweight='bold')
                    ax.grid(True, alpha=0.3)
                    st.pyplot(fig)

def show_results_page():
    """Страница результатов"""
    st.title("🏆 Результаты соревнований")
    
    results = get_sport_results(limit=100)
    
    if not results.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'competition_name' in results.columns:
                comp_filter = st.multiselect("Соревнование:", results['competition_name'].unique())
        with col2:
            if 'discipline' in results.columns:
                disc_filter = st.multiselect("Дисциплина:", results['discipline'].unique())
        with col3:
            sort_by = st.selectbox("Сортировка:", ["Дате (новые)", "Месту", "Спортсмену"])
        
        filtered = results
        if comp_filter:
            filtered = filtered[filtered['competition_name'].isin(comp_filter)]
        if disc_filter:
            filtered = filtered[filtered['discipline'].isin(disc_filter)]
        
        if sort_by == "Дате (новые)":
            filtered = filtered.sort_values('competition_date', ascending=False)
        elif sort_by == "Месту":
            if 'place' in filtered.columns:
                filtered = filtered.sort_values('place')
        
        st.dataframe(filtered, use_container_width=True, hide_index=True)
    else:
        st.info("📭 Нет результатов")

def show_settings_page():
    """Страница настроек"""
    st.title("⚙️ Настройки")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 Профиль")
        st.success(f"Текущий пользователь: **{st.session_state.get('user', {}).get('username', 'N/A')}**")
        st.info(f"Роль: **{st.session_state.get('user', {}).get('role', 'N/A')}**")
    
    with col2:
        st.subheader("📊 О системе")
        st.info("""
        **Версия:** 2.1.0 (Extended)
        
        **Дата:** 26.11.2025
        
        **Статус:** ✅ Активна
        
        **Новое:** Виды спорта, регионы, тренеры
        """)

def authenticate_user(username: str, password: str):
    """Аутентификация"""
    import bcrypt
    
    if not username or not password:
        return False
    
    user = get_user_by_username(username)
    if user is None:
        return False
    
    try:
        if bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
            st.session_state['user'] = user
            return True
    except:
        pass
    
    return False

# ==================== ЗАПУСК ====================

if __name__ == "__main__":
    main()
