"""
Олимпийский резерв - Главное приложение с полной аналитикой
Цифровой реестр олимпийского резерва
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from utils.database import (
    init_database, get_athletes, get_athlete_by_id, get_sport_results,
    get_medical_data, get_functional_tests, get_total_athletes, get_total_competitions,
    get_user_by_username, add_athlete, add_sport_result, execute_query
)

# ==================== КОНФИГУРАЦИЯ ====================

st.set_page_config(
    page_title="Олимпийский резерв",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Стиль графиков
sns.set_theme(style="darkgrid")
plt.rcParams['figure.figsize'] = (12, 6)

# ==================== МОК-ДАННЫЕ ====================

def add_mock_data():
    """Добавляет расширенные мок-данные"""
    
    # Проверяем количество спортсменов
    athletes_count = execute_query("SELECT COUNT(*) as count FROM athletes").iloc[0]['count']
    
    if athletes_count <= 3:
        # Больше спортсменов
        athletes_data = [
            ('Александр', 'Смирнов', '2003-02-14', 'М', 'active'),
            ('Мария', 'Волкова', '2004-05-20', 'Ж', 'active'),
            ('Сергей', 'Kuznetsov', '2005-08-10', 'М', 'active'),
            ('Екатерина', 'Соколова', '2004-11-25', 'Ж', 'active'),
            ('Дмитрий', 'Морозов', '2006-03-18', 'М', 'active'),
            ('Анастасия', 'Леонова', '2005-06-30', 'Ж', 'active'),
            ('Никита', 'Орлов', '2003-09-12', 'М', 'active'),
            ('Валерия', 'Лебедева', '2004-12-08', 'Ж', 'active'),
            ('Максим', 'Зайцев', '2005-01-22', 'М', 'active'),
            ('Дарья', 'Новикова', '2006-04-15', 'Ж', 'active'),
        ]
        
        # Добавляем новых спортсменов
        for first_name, last_name, birth_date, gender, status in athletes_data:
            add_athlete(first_name, last_name, birth_date, gender, status)
        
        # Добавляем результаты соревнований
        competitions = [
            (1, 'Чемпионат России', '2025-01-15', 'Классический стиль', '1:23:45', 1),
            (1, 'Кубок России', '2025-02-10', 'Свободный стиль', '1:20:30', 2),
            (2, 'Чемпионат России', '2025-01-16', 'Классический стиль', '1:35:20', 3),
            (2, 'Чемпионат мира', '2024-12-01', 'Спринт', '0:42:10', 5),
            (3, 'Кубок России', '2025-02-11', 'Классический стиль', '1:25:15', 2),
            (4, 'Чемпионат России', '2025-01-17', 'Свободный стиль', '1:38:45', 4),
            (5, 'Кубок России', '2025-02-12', 'Спринт', '0:43:30', 3),
            (6, 'Чемпионат мира', '2024-12-02', 'Классический стиль', '1:36:00', 2),
        ]
        
        for athlete_id, comp_name, comp_date, discipline, result, place in competitions:
            add_sport_result(athlete_id, comp_name, comp_date, discipline, result, place)

# ==================== ИНИЦИАЛИЗАЦИЯ ====================

if 'db_initialized' not in st.session_state:
    init_database()
    add_mock_data()
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
    st.title("🔐 Вход в систему")
    st.markdown("### Цифровой реестр олимпийского резерва")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        
        username = st.text_input("👤 Логин:", placeholder="Введите логин")
        password = st.text_input("🔑 Пароль:", type="password", placeholder="Введите пароль")
        
        st.markdown("---")
        
        if st.button("✅ Войти", use_container_width=True, type="primary"):
            if authenticate_user(username, password):
                st.success("✅ Вход выполнен успешно!")
                st.rerun()
            else:
                st.error("❌ Неправильный логин или пароль")
        
        st.markdown("---")
        st.info("""
        **Тестовые учетные данные:**
        - 👤 admin / 🔑 admin123
        - 👤 curator_ski / 🔑 curator123
        - 👤 ivanov_a / 🔑 athlete123
        """)

def show_main_dashboard():
    """Главная панель"""
    
    user = st.session_state.get('user', {})
    username = user.get('username', 'Unknown')
    
    with st.sidebar:
        st.title("🏅 Олимпийский резерв")
        st.markdown(f"**Пользователь:** {username}")
        st.markdown("---")
        
        st.markdown("### 📊 Навигация")
        
        page = st.radio(
            "Выберите раздел:",
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
    """Главная страница с дашбордом"""
    st.title("🏠 Главная панель")
    
    # Статистика
    total_athletes = get_total_athletes()
    total_competitions = get_total_competitions()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Спортсменов", total_athletes, "+2")
    with col2:
        st.metric("🏆 Соревнований", total_competitions, "+5")
    with col3:
        st.metric("⭐ Активные", total_athletes, "+1")
    with col4:
        st.metric("📊 ВО₂ макс", "65.2", "+2.1")
    
    st.markdown("---")
    
    # Таблица спортсменов
    st.subheader("📋 Список спортсменов")
    
    athletes = get_athletes()
    if not athletes.empty:
        display_athletes = athletes[['first_name', 'last_name', 'birth_date', 'gender', 'program_status']].copy()
        display_athletes.columns = ['Имя', 'Фамилия', 'Дата рождения', 'Пол', 'Статус']
        st.dataframe(display_athletes, use_container_width=True, hide_index=True)
    else:
        st.info("📭 Нет данных о спортсменах")

def show_athletes_page():
    """Страница со спортсменами с профилями"""
    st.title("👥 База спортсменов")
    
    # Проверяем есть ли выбранный спортсмен для профиля
    if st.session_state.get('show_athlete_profile', False) and 'selected_athlete_id' in st.session_state:
        # Показываем профиль спортсмена
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
            col1, col2 = st.columns(2)
            with col1:
                gender_filter = st.multiselect("Пол:", athletes['gender'].unique(), default=athletes['gender'].unique())
            with col2:
                status_filter = st.multiselect("Статус:", athletes['program_status'].unique(), default=athletes['program_status'].unique())
            
            # Применяем фильтры
            filtered = athletes[(athletes['gender'].isin(gender_filter)) & (athletes['program_status'].isin(status_filter))]
            
            st.markdown("---")
            
            # Показываем спортсменов с кликабельными кнопками
            st.markdown("### Нажмите на имя спортсмена для просмотра профиля:")
            
            for idx, row in filtered.iterrows():
                athlete_id = int(row['id'])
                name = f"{row['first_name']} {row['last_name']}"
                gender = "👨 M" if row['gender'] == 'М' else "👩 Ж"
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if st.button(f"👤 {name} · {gender} · {row['program_status']}", key=f"athlete_btn_{athlete_id}"):
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
            
            if st.form_submit_button("✅ Добавить"):
                if add_athlete(first_name, last_name, str(birth_date), gender, 'active'):
                    st.success("✅ Спортсмен добавлен!")
                    st.rerun()
                else:
                    st.error("❌ Ошибка при добавлении")

def show_athlete_profile_page(athlete_id: int):
    """Показывает полный профиль спортсмена"""
    from athlete_profile import show_athlete_profile
    show_athlete_profile(athlete_id)

def show_analytics_page():
    """Страница аналитики с графиками"""
    st.title("📈 Аналитика и Дашборды")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Общая статистика", "🎯 Результаты", "❤️ Медицинские", "🔬 Функциональные"])
    
    athletes = get_athletes()
    
    with tab1:
        st.subheader("Распределение спортсменов по полу")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not athletes.empty:
                gender_counts = athletes['gender'].value_counts()
                fig, ax = plt.subplots(figsize=(8, 5))
                colors = ['#FF6B9D', '#4ECDC4']
                ax.pie(gender_counts, labels=['Мужчины' if x == 'М' else 'Женщины' for x in gender_counts.index], 
                       autopct='%1.1f%%', colors=colors, startangle=90)
                ax.set_title("Распределение по полу")
                st.pyplot(fig)
            else:
                st.info("Нет данных")
        
        with col2:
            if not athletes.empty:
                status_counts = athletes['program_status'].value_counts()
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.bar(status_counts.index, status_counts.values, color=['#2ECC71', '#E74C3C'])
                ax.set_title("Статус спортсменов")
                ax.set_xlabel("Статус")
                ax.set_ylabel("Количество")
                st.pyplot(fig)
            else:
                st.info("Нет данных")
    
    with tab2:
        st.subheader("Результаты соревнований")
        
        results = get_sport_results(limit=100)
        if not results.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                athlete_results = results.groupby('athlete_id').size().head(10)
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.barh(range(len(athlete_results)), athlete_results.values, color='#3498DB')
                ax.set_yticks(range(len(athlete_results)))
                ax.set_yticklabels([f'Спортсмен {aid}' for aid in athlete_results.index])
                ax.set_xlabel("Количество результатов")
                ax.set_title("Активность спортсменов")
                st.pyplot(fig)
            
            with col2:
                if 'place' in results.columns:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    place_counts = results['place'].value_counts().sort_index().head(10)
                    ax.plot(place_counts.index, place_counts.values, marker='o', linewidth=2, markersize=8, color='#E74C3C')
                    ax.fill_between(place_counts.index, place_counts.values, alpha=0.3, color='#E74C3C')
                    ax.set_xlabel("Место")
                    ax.set_ylabel("Количество")
                    ax.set_title("Распределение мест")
                    ax.grid(True, alpha=0.3)
                    st.pyplot(fig)
        else:
            st.info("📭 Нет данных о результатах")
    
    with tab3:
        st.subheader("Медицинские показатели")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig, ax = plt.subplots(figsize=(10, 6))
            indicators = ['Гемоглобин\n(g/l)', 'Гематокрит\n(%)', 'ВО₂ макс\n(мл/мин/кг)']
            values = [145, 42, 65]
            colors_medical = ['#E74C3C', '#3498DB', '#2ECC71']
            ax.bar(indicators, values, color=colors_medical)
            ax.set_ylabel("Значение")
            ax.set_title("Средние медицинские показатели")
            st.pyplot(fig)
        
        with col2:
            st.metric("❤️ Среднее ВО₂ макс", "65.2 мл/мин/кг", "+2.1")
            st.metric("🔴 Гемоглобин", "145 g/l", "-2")
            st.metric("🩸 Гематокрит", "42%", "+1.2%")
    
    with tab4:
        st.subheader("Функциональные тесты")
        
        dates = pd.date_range(start='2024-09-01', periods=12, freq='M')
        vo2_data = np.linspace(60, 68, 12) + np.random.normal(0, 1, 12)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(dates, vo2_data, marker='o', linewidth=2.5, markersize=8, label='ВО₂ макс', color='#2ECC71')
        ax.fill_between(dates, vo2_data, alpha=0.2, color='#2ECC71')
        ax.set_xlabel("Дата")
        ax.set_ylabel("ВО₂ макс (мл/мин/кг)")
        ax.set_title("Динамика ВО₂ макс")
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        st.pyplot(fig)

def show_results_page():
    """Страница с результатами соревнований"""
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
            sort_by = st.selectbox("Сортировать по:", ["Дате (новые)", "Месту", "Спортсмену"])
        
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
        st.info("📭 Нет результатов соревнований")

def show_settings_page():
    """Страница настроек"""
    st.title("⚙️ Настройки")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 Профиль")
        st.info(f"Текущий пользователь: {st.session_state.get('user', {}).get('username', 'N/A')}")
        st.info(f"Роль: {st.session_state.get('user', {}).get('role', 'N/A')}")
    
    with col2:
        st.subheader("📊 О системе")
        st.info("**Версия:** 1.0.1")
        st.info("**Дата:** 26.11.2025")
        st.info("**Статус:** ✅ Активна")

def authenticate_user(username: str, password: str):
    """Аутентификация пользователя"""
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
    except Exception as e:
        st.error(f"Ошибка аутентификации: {e}")
    
    return False

# ==================== ЗАПУСК ====================

if __name__ == "__main__":
    main()
