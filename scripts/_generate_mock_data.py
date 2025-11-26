"""
Генератор мок-данных для БД олимпийского резерва
с русскими именами и реалистичными спортивными данными
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict

# Русские имена
MALE_FIRST_NAMES = [
    "Алексей", "Артём", "Вадим", "Владимир", "Данил", "Денис",
    "Дмитрий", "Егор", "Кирилл", "Максим", "Матвей", "Никита",
    "Олег", "Павел", "Пётр", "Роман", "Сергей", "Станислав"
]

FEMALE_FIRST_NAMES = [
    "София", "Ева", "Анна", "Мария", "Александра", "Виктория",
    "Алиса", "Полина", "Елена", "Анастасия", "Екатерина",
    "Евгения", "Нина"
]

MALE_LAST_NAMES = [
    "Иванов", "Смирнов", "Кузнецов", "Попов", "Васильев",
    "Петров", "Соколов", "Михайлов", "Новиков", "Фёдоров",
    "Морозов", "Волков", "Алексеев", "Лебедев", "Семёнов",
    "Егоров", "Павлов", "Степанов", "Николаев"
]

FEMALE_LAST_NAMES = [
    "Иванова", "Смирнова", "Кузнецова", "Попова", "Васильева",
    "Петрова", "Соколова", "Михайлова", "Новикова", "Фёдорова",
    "Морозова", "Волкова", "Алексеева", "Лебедева", "Семёнова",
    "Егорова", "Павлова", "Степанова", "Николаева"
]

MALE_COACH_NAMES = [
    "Иван Сергеевич", "Петр Владимирович", "Сергей Алексеевич",
    "Владимир Юрьевич", "Дмитрий Константинович"
]

FEMALE_COACH_NAMES = [
    "Мария Ивановна", "Елена Петровна", "Ольга Сергеевна",
    "Анна Владимировна", "Екатерина Юрьевна"
]

SPORTS = [
    "Лёгкая атлетика",
    "Плавание",
    "Лыжные гонки",
    "Биатлон",
    "Гребля",
    "Велоспорт",
    "Конькобежный спорт",
    "Горнолыжный спорт",
    "Гимнастика",
    "Волейбол"
]

RUSSIAN_REGIONS = [
    "Москва", "Санкт-Петербург", "Свердловская область", "Краснодарский край",
    "Республика Татарстан", "Новосибирская область", "Нижегородская область",
    "Ханты-Мансийский АО", "Челябинская область", "Пермский край",
    "Республика Башкортостан", "Иркутская область", "Кемеровская область",
    "Респ. Саха (Якутия)", "Оренбургская область", "Ямало-Ненецкий АО",
    "Тюменская область", "Томская область", "Республика Коми"
]

COMPETITION_NAMES = [
    "Чемпионат России", "Первенство России", "ФСПУ", "Кубок России",
    "Чемпионат Европы", "Чемпионат мира", "Олимпийские игры",
    "Европейские игры", "Международное турниры"
]

EVENTS = {
    "Лёгкая атлетика": [
        "100 м", "200 м", "400 м", "800 м", "1500 м", "5000 м",
        "Прыжок в длину", "Прыжок в высоту", "Толкание ядра"
    ],
    "Плавание": [
        "50 м вольный стиль", "100 м вольный стиль", "200 м вольный стиль",
        "100 м брасс", "200 м брасс", "100 м спина", "200 м спина"
    ],
    "Лыжные гонки": [
        "1 км", "5 км", "10 км", "15 км", "30 км", "Марафон"
    ],
    "Биатлон": [
        "Спринт 10 км", "Спринт 7.5 км", "Преследование 12.5 км", "Индивидуальная 20 км"
    ],
    "Гребля": [
        "Распашная пара", "Распашная четвёрка", "Распашная восьмёрка", "Двойка без рулевого"
    ]
}


def generate_athlete_name(gender: str = None) -> tuple:
    """Генерировать ФИО спортсмена"""
    if gender is None:
        gender = random.choice(["M", "F"])
    
    if gender == "M":
        first_name = random.choice(MALE_FIRST_NAMES)
        last_name = random.choice(MALE_LAST_NAMES)
    else:
        first_name = random.choice(FEMALE_FIRST_NAMES)
        last_name = random.choice(FEMALE_LAST_NAMES)
    
    full_name = f"{first_name} {last_name}"
    return full_name, gender


def generate_athletes(count: int = 30) -> List[Dict]:
    """Генерировать данные спортсменов"""
    athletes = []
    
    for _ in range(count):
        full_name, gender = generate_athlete_name()
        sport = random.choice(SPORTS)
        
        # Выбрать тренера
        if gender == "M":
            coach = random.choice(MALE_COACH_NAMES)
        else:
            coach = random.choice(FEMALE_COACH_NAMES)
        
        # Дата рождения (15-22 года)
        years_back = random.randint(15, 22)
        birth_date = datetime.now() - timedelta(days=365*years_back + random.randint(1, 365))
        
        # Дата включения в программу (1-3 года назад)
        enrollment_date = datetime.now() - timedelta(days=random.randint(365, 1095))
        
        athlete = {
            "full_name": full_name,
            "birth_date": birth_date.date(),
            "gender": gender,
            "email": f"{full_name.lower().replace(' ', '.')}@athlete.ru",
            "phone": f"+7 ({random.randint(900,999)}) {random.randint(100,999)}-{random.randint(10,99)}-{random.randint(10,99)}",
            "sport": sport,
            "federation": f"Федерация {sport}",
            "region": random.choice(RUSSIAN_REGIONS),
            "personal_coach": coach,
            "enrollment_date": enrollment_date.date(),
            "status": random.choice(["active", "active", "active", "inactive"]),  # 75% active
            "target_rank": random.choice(["КМС", "МС", "ЗМС", "МСМК"]),
            "target_achievement": f"Выйти на чемпионат России"
        }
        
        athletes.append(athlete)
    
    return athletes


def generate_competition_results(athlete_id: int, num_results: int = 15) -> List[Dict]:
    """Генерировать результаты соревнований для спортсмена"""
    results = []
    
    # Получить информацию о спортсмене из контекста (нужна БД для этого)
    # Генерируем результаты за последние 2 года
    
    for i in range(num_results):
        days_back = random.randint(0, 730)  # 2 года
        comp_date = datetime.now() - timedelta(days=days_back)
        
        result = {
            "athlete_id": athlete_id,
            "competition_name": random.choice(COMPETITION_NAMES),
            "competition_date": comp_date.date(),
            "competition_level": random.choice(["international", "national", "regional"]),
            "distance_or_event": "100 м",  # Упрощённо, в реальности нужно связать со спортом
            "result": round(random.uniform(10.5, 13.5), 2),  # Время в секундах
            "unit": "сек",
            "place": random.randint(1, 10),
            "personal_best": random.choice([True, False, False, False]),  # 25% личный рекорд
            "notes": None
        }
        
        results.append(result)
    
    return results


def generate_medical_data(athlete_id: int, num_records: int = 10) -> List[Dict]:
    """Генерировать медико-биологические показатели"""
    medical_records = []
    
    for i in range(num_records):
        days_back = random.randint(0, 730)
        measure_date = datetime.now() - timedelta(days=days_back)
        
        # Генерировать реалистичные показатели для спортсмена высокого уровня
        
        # ЧСС (уд/мин)
        resting_hr = random.randint(45, 65)  # В покое
        max_hr = random.randint(190, 210)
        
        # МПК (мл/мин и мл/кг/мин)
        vo2max_abs = random.uniform(4000, 5500)  # Абсолютный
        vo2max_rel = random.uniform(60, 85)  # Относительный
        
        # ПАНО (% от МПК)
        anaerobic = random.uniform(85, 95)
        
        # Пульсовые зоны (по Карвонену)
        zone_1 = f"{int(resting_hr + (max_hr - resting_hr) * 0.50)}-{int(resting_hr + (max_hr - resting_hr) * 0.60)}"
        zone_2 = f"{int(resting_hr + (max_hr - resting_hr) * 0.60)}-{int(resting_hr + (max_hr - resting_hr) * 0.70)}"
        zone_3 = f"{int(resting_hr + (max_hr - resting_hr) * 0.70)}-{int(resting_hr + (max_hr - resting_hr) * 0.80)}"
        zone_4 = f"{int(resting_hr + (max_hr - resting_hr) * 0.80)}-{int(resting_hr + (max_hr - resting_hr) * 0.90)}"
        zone_5 = f"{int(resting_hr + (max_hr - resting_hr) * 0.90)}-{max_hr}"
        
        # Морфометрия
        height = random.randint(165, 195)  # см
        weight = random.randint(60, 85)  # кг
        lean_mass = weight * random.uniform(0.85, 0.92)
        fat_pct = ((weight - lean_mass) / weight) * 100
        
        # Динамометрия
        grip_left = random.randint(40, 60)
        grip_right = random.randint(42, 65)
        
        # Кровь
        hemoglobin = round(random.uniform(13.5, 16.0), 1)  # г/дл
        hematocrit = round(random.uniform(40, 50), 1)  # %
        lactate = round(random.uniform(2.0, 4.0), 1)  # ммоль/л
        
        # Лёгкие
        lung_volume = random.randint(4500, 6000)  # мл
        
        record = {
            "athlete_id": athlete_id,
            "measurement_date": measure_date.date(),
            "doctor_name": random.choice(["Др. Петров И.И.", "Др. Соколова М.М.", "Др. Морозов А.А."]),
            "resting_heart_rate": resting_hr,
            "max_heart_rate": max_hr,
            "vo2max": round(vo2max_abs, 0),
            "vo2max_relative": round(vo2max_rel, 1),
            "anaerobic_threshold": round(anaerobic, 1),
            "zone_1_heart_rate": zone_1,
            "zone_2_heart_rate": zone_2,
            "zone_3_heart_rate": zone_3,
            "zone_4_heart_rate": zone_4,
            "zone_5_heart_rate": zone_5,
            "height": height,
            "weight": weight,
            "lean_mass": round(lean_mass, 1),
            "fat_percentage": round(fat_pct, 1),
            "hand_grip_left": grip_left,
            "hand_grip_right": grip_right,
            "hemoglobin": hemoglobin,
            "hematocrit": hematocrit,
            "lactate": lactate,
            "lung_volume": lung_volume,
            "doctor_recommendations": "Хорошие показатели. Рекомендуется увеличить объём аэробных тренировок."
        }
        
        medical_records.append(record)
    
    return medical_records
