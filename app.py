import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Добавь пути для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.auth import authenticate_user, init_session_state
from utils.rbac import check_access, get_user_sports
from database.connection import get_db_session

# Конфиг страницы
st.set_page_config(
    page_title="Цифровой реестр олимпийского резерва",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS оформление
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .header-title {
        color: #1f4788;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

# Инициализация сессии
init_session_state()

# Проверка аутентификации
if "user" not in st.session_state or st.session_state.user is None:
    # Страница входа
    st.markdown('<h1 class="header-title">🏅 Цифровой реестр олимпийского резерва</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Защищённый портал управления профилями спортсменов
        
        Компоненты системы:
        - **База данных олимпийского резерва** — информация о спортсменах, статусы, федерации
        - **Цифровой профиль спортсмена** — спортивные результаты, медико-биологические показатели
        - **Аналитика и отчёты** — динамика показателей за 2 года, графики развития
        """)
    
    with col2:
        st.info("👤 Используй учётные данные из README.md для входа")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        email = st.text_input("📧 Email", key="login_email")
    
    with col2:
        password = st.text_input("🔐 Пароль", type="password", key="login_password")
    
    with col3:
        if st.button("🔓 Вход", use_container_width=True, key="login_btn"):
            user = authenticate_user(email, password)
            if user:
                st.session_state.user = user
                st.session_state.authenticated = True
                st.success(f"✅ Добро пожаловать, {user['full_name']}!")
                st.rerun()
            else:
                st.error("❌ Неверный email или пароль")
    
    st.markdown("""
    <div class="info-box">
    <strong>🧪 Тестовые учётные данные:</strong><br>
    <code>admin@ocr.ru / admin123</code><br>
    <code>curator_athletics@ocr.ru / curator123</code><br>
    <code>athlete@example.com / athlete123</code>
    </div>
    """, unsafe_allow_html=True)

else:
    # Основное приложение
    # Сайдбар с меню
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user['full_name']}")
        st.markdown(f"**Роль:** {st.session_state.user['role']}")
        st.divider()
        
        if st.button("🚪 Выход", use_container_width=True, key="logout_btn"):
            st.session_state.user = None
            st.session_state.authenticated = False
            st.rerun()
    
    # Главная страница
    st.markdown(f'<h1 class="header-title">🏅 Цифровой реестр олимпийского резерва</h1>', unsafe_allow_html=True)
    
    # Главная панель для администратора
    if st.session_state.user['role'] == 'admin':
        st.markdown("## 📊 Панель администратора")
        
        session = get_db_session()
        
        # Статистика
        from database.models import Athlete, CompetitionResult, MedicalData
        
        total_athletes = session.query(Athlete).count()
        total_results = session.query(CompetitionResult).count()
        total_medical_records = session.query(MedicalData).count()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <h3 style="margin-top: 0;">👥 Спортсменов</h3>
                <h2 style="margin: 0.5rem 0;">{total_athletes}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <h3 style="margin-top: 0;">🏆 Результатов</h3>
                <h2 style="margin: 0.5rem 0;">{total_results}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <h3 style="margin-top: 0;">🏥 Медицинских данных</h3>
                <h2 style="margin: 0.5rem 0;">{total_medical_records}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            last_update = session.query(Athlete).order_by(Athlete.updated_at.desc()).first()
            if last_update:
                update_date = last_update.updated_at.strftime("%d.%m.%Y")
            else:
                update_date = "—"
            st.markdown(f"""
            <div class="stat-card">
                <h3 style="margin-top: 0;">📅 Последнее обновление</h3>
                <h2 style="margin: 0.5rem 0;">{update_date}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        session.close()
        
        st.divider()
        
        tab1, tab2, tab3 = st.tabs(["📈 Статистика", "👥 Спортсмены", "⚙️ Администрирование"])
        
        with tab1:
            st.markdown("### Распределение спортсменов по видам спорта")
            session = get_db_session()
            
            athletes_by_sport = session.query(
                Athlete.sport,
                session.func.count(Athlete.id).label('count')
            ).group_by(Athlete.sport).all()
            
            if athletes_by_sport:
                df_sports = pd.DataFrame(athletes_by_sport, columns=['Вид спорта', 'Количество'])
                st.bar_chart(df_sports.set_index('Вид спорта'))
            
            session.close()
        
        with tab2:
            st.markdown("### Список спортсменов")
            session = get_db_session()
            
            athletes = session.query(Athlete).all()
            
            if athletes:
                df_athletes = pd.DataFrame([
                    {
                        'ФИО': a.full_name,
                        'Вид спорта': a.sport,
                        'Федерация': a.federation,
                        'Регион': a.region,
                        'Тренер': a.personal_coach,
                        'Дата включения': a.enrollment_date.strftime("%d.%m.%Y") if a.enrollment_date else "—"
                    }
                    for a in athletes
                ])
                
                st.dataframe(df_athletes, use_container_width=True)
            else:
                st.info("Спортсменов в базе не найдено")
            
            session.close()
        
        with tab3:
            st.markdown("### Управление системой")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Пересоздать мок-данные", key="recreate_mock"):
                    st.info("Для пересоздания мок-данных запусти: `python scripts/init_db.py`")
            
            with col2:
                if st.button("📊 Экспортировать отчёт", key="export_report"):
                    st.info("Функция экспорта в разработке")

    # Главная для куратора
    elif st.session_state.user['role'] == 'curator':
        st.markdown("## 📋 Панель куратора")
        st.info(f"Вы ответственны за: {', '.join(get_user_sports(st.session_state.user['user_id']))}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="info-box">
            <strong>✅ Доступные действия:</strong><br>
            • Просмотр спортсменов своего вида спорта<br>
            • Добавление результатов соревнований<br>
            • Обновление медико-биологических показателей<br>
            • Комментирование динамики
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="info-box warning-box">
            <strong>ℹ️ Ограничения:</strong><br>
            • Невозможно удалять данные<br>
            • Доступ только к своему виду спорта<br>
            • Не видите тренировочные плаы других видов спорта
            </div>
            """, unsafe_allow_html=True)
    
    # Главная для спортсмена
    elif st.session_state.user['role'] == 'athlete':
        st.markdown("## 👤 Мой профиль")
        st.info("Здесь вы можете просматривать свои спортивные результаты, медико-биологические показатели и планы развития.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="success-box info-box">
            <strong>📖 Содержание профиля:</strong><br>
            • Персональные данные<br>
            • Спортивные результаты за 2 года<br>
            • Медико-биологические показатели<br>
            • План развития
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="info-box">
            <strong>🔒 Режим доступа:</strong><br>
            Только для просмотра (read-only)<br>
            Редактирование может быть выполнено только кураторами ОКР
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    pass
