"""
Олимпийский резерв - Главное приложение
Цифровой реестр олимпийского резерва
"""

import streamlit as st
import pandas as pd
from utils.database import init_database, get_athletes, get_total_athletes, get_total_competitions

# ==================== КОНФИГУРАЦИЯ ====================

st.set_page_config(
    page_title="Олимпийский резерв",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== ИНИЦИАЛИЗАЦИЯ ====================

# Инициализируем БД при первом запуске
if 'db_initialized' not in st.session_state:
    init_database()
    st.session_state.db_initialized = True

# ==================== ГЛАВНАЯ СТРАНИЦА ====================

def main():
    """Главная функция приложения"""
    
    # Проверяем аутентификацию
    if 'user' not in st.session_state:
        show_login_page()
        return
    
    # Если пользователь авторизован - показываем главную панель
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
    
    # Боковое меню
    with st.sidebar:
        st.title("🏅 Олимпийский резерв")
        st.markdown(f"**Пользователь:** {username}")
        st.markdown("---")
        
        st.markdown("### 📊 Навигация")
        
        page = st.radio(
            "Выберите раздел:",
            ["🏠 Главная", "👥 База спортсменов", "📈 Аналитика", "⚙️ Настройки"],
            index=0
        )
        
        st.markdown("---")
        
        if st.button("🚪 Выход", use_container_width=True):
            if 'user' in st.session_state:
                del st.session_state['user']
            st.rerun()
    
    # Основной контент
    if page == "🏠 Главная":
        show_home_page()
    elif page == "👥 База спортсменов":
        show_athletes_page()
    elif page == "📈 Аналитика":
        show_analytics_page()
    elif page == "⚙️ Настройки":
        show_settings_page()

def show_home_page():
    """Главная страница"""
    st.title("🏠 Главная панель")
    
    col1, col2, col3 = st.columns(3)
    
    # Общая статистика
    total_athletes = get_total_athletes()
    total_competitions = get_total_competitions()
    
    with col1:
        st.metric(
            label="👥 Всего спортсменов",
            value=total_athletes,
            delta=None
        )
    
    with col2:
        st.metric(
            label="🏆 Соревнований",
            value=total_competitions,
            delta=None
        )
    
    with col3:
        st.metric(
            label="⭐ Активные",
            value=total_athletes,
            delta=None
        )
    
    st.markdown("---")
    
    # Последние спортсмены
    st.subheader("📋 Последние спортсмены")
    
    athletes = get_athletes()
    if not athletes.empty:
        st.dataframe(
            athletes[['first_name', 'last_name', 'birth_date', 'gender', 'program_status']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("📭 Нет данных о спортсменах")

def show_athletes_page():
    """Страница со спортсменами"""
    st.title("👥 База спортсменов")
    
    tab1, tab2 = st.tabs(["📋 Список", "➕ Добавить"])
    
    with tab1:
        st.subheader("Список всех спортсменов")
        
        athletes = get_athletes()
        if not athletes.empty:
            st.dataframe(athletes, use_container_width=True, hide_index=True)
        else:
            st.info("📭 Нет данных о спортсменах")
    
    with tab2:
        st.subheader("Добавить нового спортсмена")
        
        with st.form("add_athlete_form"):
            first_name = st.text_input("Имя:")
            last_name = st.text_input("Фамилия:")
            birth_date = st.date_input("Дата рождения:")
            gender = st.selectbox("Пол:", ["М", "Ж"])
            
            if st.form_submit_button("✅ Добавить"):
                st.success("✅ Спортсмен добавлен!")

def show_analytics_page():
    """Страница аналитики"""
    st.title("📈 Аналитика")
    
    st.info("📊 Раздел аналитики находится в разработке")

def show_settings_page():
    """Страница настроек"""
    st.title("⚙️ Настройки")
    
    st.info("⚙️ Раздел настроек находится в разработке")

def authenticate_user(username: str, password: str):
    """Аутентификация пользователя"""
    from utils.database import get_user_by_username
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
