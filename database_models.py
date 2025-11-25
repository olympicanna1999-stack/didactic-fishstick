from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Athlete(Base):
    """Профиль спортсмена"""
    __tablename__ = "athletes"
    
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)  # M, F
    email = Column(String(255), unique=True)
    phone = Column(String(20))
    
    # Спортивная информация
    sport = Column(String(100), nullable=False)  # Вид спорта
    federation = Column(String(255))  # Федерация
    region = Column(String(255), nullable=False)  # Регион, за который выступает
    personal_coach = Column(String(255))
    
    # Статус в программе
    enrollment_date = Column(Date, nullable=False)
    status = Column(String(50), default="active")  # active, inactive, graduated
    
    # Целевые ориентиры
    target_rank = Column(String(100))  # Разряд
    target_achievement = Column(String(255))  # Целевой результат
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CompetitionResult(Base):
    """Результаты соревнований"""
    __tablename__ = "competition_results"
    
    id = Column(Integer, primary_key=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id"), nullable=False)
    
    competition_name = Column(String(255), nullable=False)
    competition_date = Column(Date, nullable=False)
    competition_level = Column(String(50))  # international, national, regional
    
    # Результаты
    distance_or_event = Column(String(100))  # Дистанция/упражнение
    result = Column(Float)  # Результат (время в сек или расстояние в м, баллы и т.д.)
    unit = Column(String(50))  # сек, м, баллы
    place = Column(Integer)  # Место
    
    personal_best = Column(Boolean, default=False)
    
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class MedicalData(Base):
    """Медико-биологические показатели"""
    __tablename__ = "medical_data"
    
    id = Column(Integer, primary_key=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id"), nullable=False)
    
    measurement_date = Column(Date, nullable=False)
    doctor_name = Column(String(255))
    
    # Функциональные показатели
    resting_heart_rate = Column(Integer)  # ЧСС в покое (уд/мин)
    max_heart_rate = Column(Integer)  # Максимальная ЧСС
    vo2max = Column(Float)  # МПК абсолютный (мл/мин)
    vo2max_relative = Column(Float)  # МПК относительный (мл/кг/мин)
    anaerobic_threshold = Column(Float)  # ПАНО (% от МПК)
    
    # Пульсовые зоны
    zone_1_heart_rate = Column(String(50))  # Зона 1 (восстановление)
    zone_2_heart_rate = Column(String(50))  # Зона 2 (аэробная)
    zone_3_heart_rate = Column(String(50))  # Зона 3 (пороговая)
    zone_4_heart_rate = Column(String(50))  # Зона 4 (анаэробная)
    zone_5_heart_rate = Column(String(50))  # Зона 5 (максимальная)
    
    # Морфометрия
    height = Column(Float)  # Рост (см)
    weight = Column(Float)  # Вес (кг)
    lean_mass = Column(Float)  # Безжировая масса (кг)
    fat_percentage = Column(Float)  # % жира
    
    # Силовые показатели
    hand_grip_left = Column(Float)  # Динамометрия левая (кг)
    hand_grip_right = Column(Float)  # Динамометрия правая (кг)
    
    # Кровь
    hemoglobin = Column(Float)  # Гемоглобин (г/дл)
    hematocrit = Column(Float)  # Гематокрит (%)
    lactate = Column(Float)  # Лактат (ммоль/л)
    
    # Лёгкие
    lung_volume = Column(Float)  # Объём лёгких (мл)
    
    # Примечания
    doctor_recommendations = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class DevelopmentPlan(Base):
    """Индивидуальный план развития"""
    __tablename__ = "development_plans"
    
    id = Column(Integer, primary_key=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id"), nullable=False)
    
    period_start = Column(Date, nullable=False)  # Начало периода
    period_end = Column(Date, nullable=False)  # Конец периода
    
    # Цели
    primary_goal = Column(String(255))
    secondary_goals = Column(Text)  # JSON или текст с целями
    
    # Задачи на период
    tasks_3_months = Column(Text)
    tasks_6_months = Column(Text)
    tasks_12_months = Column(Text)
    
    # Метрики прогресса
    metrics = Column(Text)  # JSON с метриками
    
    # Поддержка
    support_measures = Column(Text)  # Требуемая поддержка
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base):
    """Пользователи системы"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    
    role = Column(String(50), nullable=False)  # admin, curator, athlete
    sports = Column(String(500))  # JSON список видов спорта для куратора
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    """Лог всех действий с данными"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(50), nullable=False)  # CREATE, READ, UPDATE, DELETE
    table_name = Column(String(100), nullable=False)
    record_id = Column(Integer)
    changes = Column(Text)  # JSON с изменениями
    ip_address = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)
