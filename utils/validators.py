"""
Валидаторы входных данных
"""

from datetime import datetime, date
import re


def validate_email(email: str) -> bool:
    """Валидация email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Валидация телефона"""
    # Примитивная проверка
    phone_digits = re.sub(r'\D', '', phone)
    return len(phone_digits) >= 10


def validate_date(date_obj) -> bool:
    """Валидация даты"""
    if not isinstance(date_obj, (date, datetime)):
        return False
    
    # Проверка что дата не в будущем
    if isinstance(date_obj, datetime):
        return date_obj.date() <= datetime.now().date()
    return date_obj <= datetime.now().date()


def validate_athlete_data(data: dict) -> tuple[bool, list]:
    """Валидация данных спортсмена"""
    errors = []
    
    if not data.get('full_name') or len(data['full_name']) < 3:
        errors.append("ФИО должно быть не менее 3 символов")
    
    if not data.get('email') or not validate_email(data['email']):
        errors.append("Некорректный email")
    
    if not data.get('birth_date') or not validate_date(data['birth_date']):
        errors.append("Некорректная дата рождения")
    
    if not data.get('sport'):
        errors.append("Вид спорта не выбран")
    
    if not data.get('region'):
        errors.append("Регион не выбран")
    
    return len(errors) == 0, errors


def validate_medical_data(data: dict) -> tuple[bool, list]:
    """Валидация медицинских данных"""
    errors = []
    
    if not data.get('measurement_date') or not validate_date(data['measurement_date']):
        errors.append("Некорректная дата измерения")
    
    if data.get('resting_heart_rate'):
        if not (30 <= data['resting_heart_rate'] <= 100):
            errors.append("ЧСС в покое должна быть 30-100 уд/мин")
    
    if data.get('max_heart_rate'):
        if not (150 <= data['max_heart_rate'] <= 220):
            errors.append("Максимальная ЧСС должна быть 150-220 уд/мин")
    
    if data.get('height'):
        if not (130 <= data['height'] <= 220):
            errors.append("Рост должен быть 130-220 см")
    
    if data.get('weight'):
        if not (35 <= data['weight'] <= 150):
            errors.append("Вес должен быть 35-150 кг")
    
    if data.get('vo2max_relative'):
        if not (20 <= data['vo2max_relative'] <= 100):
            errors.append("МПК должен быть 20-100 мл/кг/мин")
    
    return len(errors) == 0, errors


def validate_competition_result(data: dict) -> tuple[bool, list]:
    """Валидация результата соревнования"""
    errors = []
    
    if not data.get('competition_name'):
        errors.append("Название соревнования не заполнено")
    
    if not data.get('competition_date') or not validate_date(data['competition_date']):
        errors.append("Некорректная дата соревнования")
    
    if not data.get('result') or data['result'] <= 0:
        errors.append("Результат должен быть положительным числом")
    
    if data.get('place') and (data['place'] < 1 or data['place'] > 1000):
        errors.append("Место должно быть от 1 до 1000")
    
    return len(errors) == 0, errors
