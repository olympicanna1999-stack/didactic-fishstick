"""
Олимпийский резерв - Профессиональная версия с реалистичными данными
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
    get_medical_data, get_functional_tests, get_total_athletes, get_total_competitions,
    get_user_by_username, add_athlete, add_sport_result, execute_query
)

# ==================== КОНФИГУРАЦИЯ ====================

st.set_page_config(
    page_title="🏅 Олимпийский резерв",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Улучшенный дизайн с профессиональной цветовой схемой
custom_theme = """
<style>
    :root {
        --primary: #1f77b4;
        --secondary: #ff7f0e;
        --success: #2ca02c;
        --danger: #d62728;
        --info: #17a2b8;
    }
    
    /* Главный контейнер */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Улучшенный заголовок */
    h1 {
        color: #1f2937;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
    }
    
    /* Метрики */
    .metric-container {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
        transition: transform 0.2s;
    }
    
    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Кнопки */
    .btn-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        transition: all 0.3s;
    }
    
    .btn-primary:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Карточки */
    .card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 16px;
        border-top: 3px solid #667eea;
    }
    
    /* Таблицы */
    table {
        border-collapse: collapse;
        width: 100%;
    }
    
    th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: 600;
    }
    
    tr:hover {
        background-color: #f5f7fa;
    }
</style>
"""

st.markdown(custom_theme, unsafe_allow_html=True)

# Стиль графиков
sns.set_theme(style="whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10

# ==================== РАСШИРЕННЫЕ МОК-ДАННЫЕ ====================

def add_enhanced_mock_data():
    """Добавляет реалистичные мок-данные на основе научных исследований"""
    
    athletes_count = execute_query("SELECT COUNT(*) as count FROM athletes").iloc[0]['count']
    
    if athletes_count <= 3:
        # Спортсмены с реалистичными данными (на основе исследования гребцов)
        athletes_data = [
            # Мужчины (VO2: 55-60 мл/кг/мин, HR: 195±5, рост: 180-190см)
            ('Александр', 'Смирнов', '2003-02-14', 'М', 'active'),
            ('Сергей', 'Петров', '2004-08-10', 'М', 'active'),
            ('Дмитрий', 'Морозов', '2005-03-18', 'М', 'active'),
            ('Никита', 'Орлов', '2003-09-12', 'М', 'active'),
            ('Максим', 'Зайцев', '2005-01-22', 'М', 'active'),
            ('Андрей', 'Ивановский', '2004-06-15', 'М', 'active'),
            
            # Женщины (VO2: 45-52 мл/кг/мин, HR: 188±10, рост: 168-178см)
            ('Мария', 'Волкова', '2004-05-20', 'Ж', 'active'),
            ('Екатерина', 'Соколова', '2004-11-25', 'Ж', 'active'),
            ('Анастасия', 'Леонова', '2005-06-30', 'Ж', 'active'),
            ('Валерия', 'Лебедева', '2004-12-08', 'Ж', 'active'),
            ('Дарья', 'Новикова', '2006-04-15', 'Ж', 'active'),
            ('Ольга', 'Соколова', '2005-02-28', 'Ж', 'active'),
            ('Елена', 'Кузнецова', '2004-07-10', 'Ж', 'active'),
        ]
        
        # Добавляем спортсменов
        athlete_ids = {}
        for first_name, last_name, birth_date, gender, status in athletes_data:
            athlete_id = add_athlete(first_name, last_name, birth_date, gender, status)
            athlete_ids[f"{first_name}_{last_name}"] = athlete_id
        
        # Реалистичные соревнования за 12 месяцев
        # Мужчины (6 человек x 15 результатов = 90 результатов)
        male_athletes = [1, 2, 3, 4, 5, 6]
        female_athletes = [7, 8, 9, 10, 11, 12, 13]
        
        competitions = [
            'Чемпионат России',
            'Кубок России',
            'Чемпионат Европы юниоров',
            'Чемпионат мира юниоров',
            'Спартакиада регионов',
            'Открытый чемпионат города'
        ]
        
        disciplines = [
            'Классический стиль 5км',
            'Свободный стиль 5км',
            'Спринт 1км',
            'Длинная дистанция 10км',
            'Классический стиль 10км',
            'Командная эстафета'
        ]
        
        # Генерируем результаты
        import random
        np.random.seed(42)
        random.seed(42)
        
        for athlete_id in male_athletes:
            for _ in range(15):
                comp_date = datetime.now() - timedelta(days=random.randint(1, 365))
                comp_name = random.choice(competitions)
                discipline = random.choice(disciplines)
                # Мужчины: время 4-7 минут
                time_sec = random.randint(240, 420)
                minutes = time_sec // 60
                seconds = time_sec % 60
                result_time = f"{minutes}:{seconds:02d}"
                place = random.randint(1, 8)
                
                add_sport_result(athlete_id, comp_name, comp_date.strftime('%Y-%m-%d'), 
                               discipline, result_time, place)
        
        for athlete_id in female_athletes:
            for _ in range(15):
                comp_date = datetime.now() - timedelta(days=random.randint(1, 365))
                comp_name = random.choice(competitions)
                discipline = random.choice(disciplines)
                # Женщины: время 5-9 минут
                time_sec = random.randint(300, 540)
                minutes = time_sec // 60
                seconds = time_sec % 60
                result_time = f"{minutes}:{seconds:02d}"
                place = random.randint(1, 9)
                
                add_sport_result(athlete_id, comp_name, comp_date.strftime('%Y-%m-%d'), 
                               discipline, result_time, place)

# ==================== ИНИЦИАЛИЗАЦИЯ ====================

if 'db_initialized' not in st.session_state:
    init_database()
    add_enhanced_mock_data()
    st.session_state.db_initialized = True

# ==================== ГЛАВНАЯ СТРАНИЦА ====================

def main():
    """Главная функция приложения"""
    
    if 'user' not in st.session_state:
        show_login_page()
        return
    
    show_main_dashboard()

def show_login_page():
    """Профессиональная форма входа"""
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
    """Главная панель с профессиональным дизайном"""
    
    user = st.session_state.get('user', {})
    username = user.get('username', 'Unknown')
    
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 20px 0; margin-bottom: 20px;'>
            <h2 style='margin: 0;'>🏅 Олимпийский резерв</h2>
            <p style='margin: 10px 0 0 0; color: #666;'>v1.0.3</p>
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
    """Главная страница с улучшенным дизайном"""
    st.title("🏠 Главная панель")
    
    total_athletes = get_total_athletes()
    total_competitions = get_total_competitions()
    
    # Улучшенные метрики
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "👥 Спортсменов",
            total_athletes,
            "+2",
            help="Всего активных спортсменов в программе"
        )
    with col2:
        st.metric(
            "🏆 Соревнований",
            total_competitions,
            "+12",
            help="Всего проведено соревнований за год"
        )
    with col3:
        st.metric(
            "📊 Ср. ВО₂",
            "56.2",
            "+3.1 мл/кг/мин",
            help="Средний VO2 максимум у мужчин"
        )
    with col4:
        st.metric(
            "❤️ Пульс",
            "192",
            "+5 уд/мин",
            help="Среднее максимальное ЧСС"
        )
    
    st.markdown("---")
    
    # Таблица спортсменов с улучшенным оформлением
    st.subheader("📋 Последние добавленные спортсмены")
    
    athletes = get_athletes()
    if not athletes.empty:
        # Показываем только последних 10
        display_athletes = athletes.tail(10)[['first_name', 'last_name', 'birth_date', 'gender', 'program_status']].copy()
        display_athletes.columns = ['Имя', 'Фамилия', 'Дата рождения', 'Пол', 'Статус']
        display_athletes['Пол'] = display_athletes['Пол'].apply(lambda x: '👨 Муж.' if x == 'М' else '👩 Жен.')
        display_athletes['Статус'] = display_athletes['Статус'].apply(lambda x: '✅ Активен' if x == 'active' else '⏸ Неактивен')
        
        st.dataframe(display_athletes, use_container_width=True, hide_index=True)
    else:
        st.info("📭 Нет данных о спортсменах")

def show_athletes_page():
    """Страница со спортсменами"""
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
            col1, col2 = st.columns(2)
            with col1:
                gender_filter = st.multiselect("Пол:", athletes['gender'].unique(), default=athletes['gender'].unique())
            with col2:
                status_filter = st.multiselect("Статус:", athletes['program_status'].unique(), default=athletes['program_status'].unique())
            
            filtered = athletes[(athletes['gender'].isin(gender_filter)) & (athletes['program_status'].isin(status_filter))]
            
            st.markdown("---")
            st.markdown("### Нажмите на спортсмена для просмотра профиля:")
            
            for idx, row in filtered.iterrows():
                athlete_id = int(row['id'])
                name = f"{row['first_name']} {row['last_name']}"
                gender = "👨" if row['gender'] == 'М' else "👩"
                
                if st.button(f"{gender} {name} · {row['program_status']}", key=f"athlete_btn_{athlete_id}", use_container_width=True):
                    st.session_state['selected_athlete_id'] = athlete_id
                    st.session_state['show_athlete_profile'] = True
                    st.rerun()
        else:
            st.info("📭 Нет спортсменов")
    
    with tab2:
        st.subheader("Добавить нового спортсмена")
        
        with st.form("add_athlete_form"):
            first_name = st.text_input("Имя:")
            last_name = st.text_input("Фамилия:")
            birth_date = st.date_input("Дата рождения:")
            gender = st.selectbox("Пол:", ["М", "Ж"])
            
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
    """Страница аналитики с профессиональным дизайном"""
    st.title("📈 Аналитика и Дашборды")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Общая", "🎯 Результаты", "❤️ Физиология", "🔬 VO₂"])
    
    athletes = get_athletes()
    
    with tab1:
        st.subheader("Распределение спортсменов")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not athletes.empty:
                gender_counts = athletes['gender'].value_counts()
                fig, ax = plt.subplots(figsize=(10, 6))
                colors = ['#667eea', '#f093fb']
                wedges, texts, autotexts = ax.pie(
                    gender_counts, 
                    labels=['Мужчины' if x == 'М' else 'Женщины' for x in gender_counts.index],
                    autopct='%1.1f%%',
                    colors=colors,
                    startangle=90,
                    textprops={'fontsize': 11, 'weight': 'bold'}
                )
                ax.set_title("По полу", fontsize=14, fontweight='bold', pad=20)
                st.pyplot(fig)
        
        with col2:
            if not athletes.empty:
                status_counts = athletes['program_status'].value_counts()
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.bar(status_counts.index, status_counts.values, color=['#2ecc71', '#e74c3c'], edgecolor='black', linewidth=1.5)
                ax.set_title("По статусу", fontsize=14, fontweight='bold', pad=20)
                ax.set_ylabel("Количество", fontsize=11, fontweight='bold')
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}', ha='center', va='bottom', fontweight='bold')
                st.pyplot(fig)
    
    with tab2:
        st.subheader("Результаты соревнований")
        
        results = get_sport_results(limit=100)
        if not results.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                athlete_results = results.groupby('athlete_id').size().head(10)
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.barh(range(len(athlete_results)), athlete_results.values, color='#667eea', edgecolor='black', linewidth=1.5)
                ax.set_yticks(range(len(athlete_results)))
                ax.set_yticklabels([f'Спортсмен {aid}' for aid in athlete_results.index])
                ax.set_xlabel("Количество результатов", fontsize=11, fontweight='bold')
                ax.set_title("Активность спортсменов", fontsize=14, fontweight='bold', pad=20)
                for i, bar in enumerate(bars):
                    width = bar.get_width()
                    ax.text(width, bar.get_y() + bar.get_height()/2.,
                           f'{int(width)}', ha='left', va='center', fontweight='bold')
                st.pyplot(fig)
            
            with col2:
                if 'place' in results.columns:
                    place_counts = results['place'].value_counts().sort_index().head(10)
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.plot(place_counts.index, place_counts.values, marker='o', linewidth=2.5, markersize=10,
                           color='#667eea', markerfacecolor='#f093fb', markeredgewidth=2)
                    ax.fill_between(place_counts.index, place_counts.values, alpha=0.2, color='#667eea')
                    ax.set_xlabel("Место", fontsize=11, fontweight='bold')
                    ax.set_ylabel("Количество", fontsize=11, fontweight='bold')
                    ax.set_title("Распределение мест", fontsize=14, fontweight='bold', pad=20)
                    ax.grid(True, alpha=0.3)
                    st.pyplot(fig)
        else:
            st.info("📭 Нет данных")
    
    with tab3:
        st.subheader("Физиологические показатели (на основе исследований)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig, ax = plt.subplots(figsize=(10, 6))
            indicators = ['VO₂ макс\nМуж.\n(мл/кг/мин)', 'VO₂ макс\nЖен.\n(мл/кг/мин)', 'ЧСС макс\nМуж.\n(уд/мин)', 'ЧСС макс\nЖен.\n(уд/мин)']
            values = [58.7, 48.3, 195, 188]
            colors_phys = ['#667eea', '#f093fb', '#667eea', '#f093fb']
            bars = ax.bar(indicators, values, color=colors_phys, edgecolor='black', linewidth=1.5)
            ax.set_ylabel("Значение", fontsize=11, fontweight='bold')
            ax.set_title("Средние показатели элитных спортсменов", fontsize=14, fontweight='bold', pad=20)
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}', ha='center', va='bottom', fontweight='bold')
            st.pyplot(fig)
        
        with col2:
            st.markdown("""
            ### 📊 Нормы показателей (из научного исследования)
            
            **Мужчины-гребцы:**
            - VO₂ макс: 55-60 мл/кг/мин
            - ЧСС макс: 195±5 уд/мин
            - Рост: 180-190 см
            - Масса: 70-75 кг
            
            **Женщины-гребцы:**
            - VO₂ макс: 45-52 мл/кг/мин
            - ЧСС макс: 188±10 уд/мин
            - Рост: 168-178 см
            - Масса: 60-68 кг
            
            **Гемоглобин (оба пола):**
            - Мужчины: 14-16 g/l
            - Женщины: 12-14 g/l
            """)
    
    with tab4:
        st.subheader("Динамика VO₂ максимума")
        
        dates = pd.date_range(start='2024-01-01', periods=12, freq='M')
        vo2_male = np.linspace(55, 59, 12) + np.random.normal(0, 0.5, 12)
        vo2_female = np.linspace(46, 50, 12) + np.random.normal(0, 0.5, 12)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(dates, vo2_male, marker='o', linewidth=2.5, markersize=8, label='Мужчины', color='#667eea')
        ax.plot(dates, vo2_female, marker='s', linewidth=2.5, markersize=8, label='Женщины', color='#f093fb')
        ax.fill_between(dates, vo2_male, alpha=0.2, color='#667eea')
        ax.fill_between(dates, vo2_female, alpha=0.2, color='#f093fb')
        ax.set_xlabel("Дата", fontsize=11, fontweight='bold')
        ax.set_ylabel("VO₂ макс (мл/кг/мин)", fontsize=11, fontweight='bold')
        ax.set_title("Тренд развития аэробной производительности", fontsize=14, fontweight='bold', pad=20)
        ax.legend(fontsize=11, loc='best')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
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
        **Версия:** 2.0.0 (Professional)
        
        **Дата:** 26.11.2025
        
        **Статус:** ✅ Активна
        
        **Источник данных:** Исследование физиологических показателей элитных гребцов
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
