import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import streamlit as st

# Конфиг базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./olympic_reserve.db")

# Для локальной разработки
if DATABASE_URL == "sqlite:///./olympic_reserve.db":
    DATABASE_URL = "sqlite:///./data/olympic_reserve.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@st.cache_resource
def get_engine():
    """Получить engine (кешировано)"""
    return engine


def get_db_session() -> Session:
    """Получить сессию БД"""
    return SessionLocal()


def init_db():
    """Инициализировать БД (создать таблицы)"""
    from database.models import Base
    
    # Создать директорию для БД если её нет
    os.makedirs("./data", exist_ok=True)
    
    # Создать все таблицы
    Base.metadata.create_all(bind=engine)
    print("✅ База данных инициализирована")
