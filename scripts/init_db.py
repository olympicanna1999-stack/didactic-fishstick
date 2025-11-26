#!/usr/bin/env python
"""
Скрипт инициализации БД с реалистичными мок-данными
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Добавь путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import init_db, get_db_session
from database.models import Athlete, CompetitionResult, MedicalData, DevelopmentPlan
from scripts.generate_mock_data import (
    generate_athletes, generate_competition_results, generate_medical_data
)

def populate_database():
    """Заполнить БД мок-данными"""
    print("🔄 Инициализация базы данных...")
    
    # Инициализировать таблицы
    init_db()
    
    session = get_db_session()
    
    try:
        # Проверить, не заполнена ли уже БД
        existing_athletes = session.query(Athlete).count()
        if existing_athletes > 0:
            print(f"⚠️  БД уже содержит {existing_athletes} спортсменов. Очистка...")
            session.query(CompetitionResult).delete()
            session.query(MedicalData).delete()
            session.query(DevelopmentPlan).delete()
            session.query(Athlete).delete()
            session.commit()
        
        print("📝 Генерирую мок-данные...")
        
        # Генерируем спортсменов
        athletes_data = generate_athletes(30)  # 30 спортсменов
        
        for athlete_data in athletes_data:
            athlete = Athlete(**athlete_data)
            session.add(athlete)
        
        session.commit()
        print(f"✅ Добавлено {len(athletes_data)} спортсменов")
        
        # Генерируем результаты соревнований
        athletes = session.query(Athlete).all()
        for athlete in athletes:
            results_data = generate_competition_results(athlete.id, num_results=15)
            for result_data in results_data:
                result = CompetitionResult(**result_data)
                session.add(result)
        
        session.commit()
        print(f"✅ Добавлены результаты соревнований")
        
        # Генерируем медико-биологические данные
        for athlete in athletes:
            medical_data = generate_medical_data(athlete.id, num_records=10)
            for med_data in medical_data:
                med = MedicalData(**med_data)
                session.add(med)
        
        session.commit()
        print(f"✅ Добавлены медико-биологические показатели")
        
        # Статистика
        total_athletes = session.query(Athlete).count()
        total_results = session.query(CompetitionResult).count()
        total_medical = session.query(MedicalData).count()
        
        print(f"\n📊 Итого:")
        print(f"   👥 Спортсменов: {total_athletes}")
        print(f"   🏆 Результатов: {total_results}")
        print(f"   🏥 Медицинских записей: {total_medical}")
        print(f"\n✅ База данных успешно заполнена!")
        
    except Exception as e:
        print(f"❌ Ошибка при заполнении БД: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    populate_database()
