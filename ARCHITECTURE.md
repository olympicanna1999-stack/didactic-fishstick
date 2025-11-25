# 🏗️ Архитектура и документация проекта

## 📊 Общая архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Web App                         │
│                      (app.py + pages/)                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Authentication & RBAC                     │ │
│  │         (utils/auth.py, utils/rbac.py)               │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Dashboard, Reserve DB, Athlete Profile         │ │
│  │            Chart Visualization (Plotly)               │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    SQLAlchemy ORM                           │
│              (database/models.py)                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Athlete | CompetitionResult | MedicalData | etc       │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   База данных                              │
│    SQLite (локально) или PostgreSQL (production)          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Схема БД

### Таблица: `athletes` (Спортсмены)
```
id (INT, PK)
├── full_name (VARCHAR)
├── birth_date (DATE)
├── gender (VARCHAR)
├── email (VARCHAR, UNIQUE)
├── phone (VARCHAR)
├── sport (VARCHAR)           ← Вид спорта
├── federation (VARCHAR)      ← Федерация
├── region (VARCHAR)          ← Регион РФ
├── personal_coach (VARCHAR)  ← Тренер
├── enrollment_date (DATE)    ← Дата включения
├── status (VARCHAR)          ← active/inactive
├── target_rank (VARCHAR)     ← Целевой разряд
├── target_achievement (VARCHAR)
├── created_at (DATETIME)
└── updated_at (DATETIME)
```

### Таблица: `competition_results` (Результаты соревнований)
```
id (INT, PK)
├── athlete_id (INT, FK)
├── competition_name (VARCHAR)
├── competition_date (DATE)    ← За 2 года
├── competition_level (VARCHAR) ← international/national/regional
├── distance_or_event (VARCHAR)
├── result (FLOAT)            ← Результат
├── unit (VARCHAR)            ← сек/м/баллы
├── place (INT)               ← Место
├── personal_best (BOOLEAN)
├── notes (TEXT)
└── created_at (DATETIME)
```

### Таблица: `medical_data` (Медико-биологические показатели)
```
id (INT, PK)
├── athlete_id (INT, FK)
├── measurement_date (DATE)   ← За 2 года
├── doctor_name (VARCHAR)
│
├── *** Функциональные показатели ***
├── resting_heart_rate (INT)         ← ЧСС в покое
├── max_heart_rate (INT)             ← Максимальная ЧСС
├── vo2max (FLOAT)                   ← МПК абсолютный
├── vo2max_relative (FLOAT)          ← МПК относительный
├── anaerobic_threshold (FLOAT)      ← ПАНО (%)
│
├── *** Пульсовые зоны ***
├── zone_1_heart_rate (VARCHAR)      ← Восстановление
├── zone_2_heart_rate (VARCHAR)      ← Аэробная
├── zone_3_heart_rate (VARCHAR)      ← Пороговая
├── zone_4_heart_rate (VARCHAR)      ← Анаэробная
├── zone_5_heart_rate (VARCHAR)      ← Максимальная
│
├── *** Морфометрия ***
├── height (FLOAT)                   ← Рост (см)
├── weight (FLOAT)                   ← Вес (кг)
├── lean_mass (FLOAT)                ← Безжировая масса
├── fat_percentage (FLOAT)           ← % жира
│
├── *** Силовые показатели ***
├── hand_grip_left (FLOAT)           ← Динамометрия левая
├── hand_grip_right (FLOAT)          ← Динамометрия правая
│
├── *** Кровь ***
├── hemoglobin (FLOAT)               ← Гемоглобин (г/дл)
├── hematocrit (FLOAT)               ← Гематокрит (%)
├── lactate (FLOAT)                  ← Лактат (ммоль/л)
│
├── *** Лёгкие ***
├── lung_volume (FLOAT)              ← Объём лёгких (мл)
│
├── doctor_recommendations (TEXT)
└── created_at (DATETIME)
```

### Таблица: `development_plans` (Планы развития)
```
id (INT, PK)
├── athlete_id (INT, FK)
├── period_start (DATE)
├── period_end (DATE)
├── primary_goal (VARCHAR)
├── secondary_goals (TEXT)
├── tasks_3_months (TEXT)
├── tasks_6_months (TEXT)
├── tasks_12_months (TEXT)
├── metrics (TEXT)              ← JSON
├── support_measures (TEXT)
├── created_at (DATETIME)
└── updated_at (DATETIME)
```

### Таблица: `users` (Пользователи системы)
```
id (INT, PK)
├── email (VARCHAR, UNIQUE)
├── password_hash (VARCHAR)
├── full_name (VARCHAR)
├── role (VARCHAR)              ← admin/curator/athlete
├── sports (VARCHAR)            ← JSON для кураторов
├── is_active (BOOLEAN)
├── created_at (DATETIME)
└── updated_at (DATETIME)
```

### Таблица: `audit_logs` (Логирование действий)
```
id (INT, PK)
├── user_id (INT, FK)
├── action (VARCHAR)            ← CREATE/READ/UPDATE/DELETE
├── table_name (VARCHAR)
├── record_id (INT)
├── changes (TEXT)              ← JSON с изменениями
├── ip_address (VARCHAR)
└── timestamp (DATETIME)
```

---

## 🔐 Система аутентификации и RBAC

### Уровни доступа

```
┌─────────────────────────────────────────────────────────┐
│                    АДМИНИСТРАТОР                        │
│  ✅ Просмотр всех данных                               │
│  ✅ Редактирование всех данных                         │
│  ✅ Удаление данных                                    │
│  ✅ Управление пользователями                          │
│  ✅ Экспорт отчётов                                    │
│  ✅ Аналитика по всем видам спорта                    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              КУРАТОР ПО ВИДУ СПОРТА                     │
│  ✅ Просмотр своего вида спорта                         │
│  ✅ Редактирование результатов                         │
│  ✅ Обновление мед. показателей                        │
│  ✅ Комментирование прогресса                          │
│  ❌ Удаление данных                                    │
│  ❌ Управление пользователями                          │
│  ❌ Доступ к другим видам спорта                       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│            СПОРТСМЕН / РОДИТЕЛЬ                        │
│  ✅ Просмотр своего профиля                            │
│  ✅ Просмотр результатов                               │
│  ✅ Просмотр графиков развития                         │
│  ❌ Редактирование данных                              │
│  ❌ Просмотр данных других спортсменов                 │
└─────────────────────────────────────────────────────────┘
```

### Матрица прав доступа

| Функция | Admin | Curator | Athlete |
|---------|-------|---------|---------|
| Просмотр спортсмена | ✅ | ✅* | ✅** |
| Редактирование профиля | ✅ | ✅* | ❌ |
| Добавление результата | ✅ | ✅* | ❌ |
| Обновление мед. данных | ✅ | ✅* | ❌ |
| Удаление данных | ✅ | ❌ | ❌ |
| Просмотр аналитики | ✅ | ✅* | ❌ |
| Управление пользователями | ✅ | ❌ | ❌ |
| Экспорт данных | ✅ | ✅* | ❌ |

**Легенда:** ✅ = доступно, ❌ = недоступно, ✅* = только своего вида спорта, ✅** = только свой профиль

---

## 📊 Компоненты визуализации

### Графики, которые генерирует приложение

1. **📈 Динамика результатов соревнований** (2 года)
   - X: Дата соревнования
   - Y: Результат
   - Тип: Line + Markers

2. **📊 МПК (VO2max)**
   - МПК абсолютный (мл/мин)
   - МПК относительный (мл/кг/мин)
   - Тренд за 2 года

3. **🫀 Пульсовые зоны**
   - 5 зон (восстановление → максимум)
   - Горизонтальная диаграмма

4. **⚖️ Морфометрические показатели**
   - Вес (кг)
   - % жира
   - Двойная ось Y

5. **🧬 Показатели крови**
   - Гемоглобин
   - Гематокрит
   - Лактат (метрики)

6. **📍 Распределение спортсменов**
   - По видам спорта (столбчатая диаграмма)
   - По регионам (карта, опционально)

---

## 🔄 Процесс добавления нового спортсмена

```
Админ/Куратор → Нажать "Добавить спортсмена"
                    ↓
            Заполнить форму
            (ФИО, дата рождения, вид спорта, регион)
                    ↓
            Валидация данных (validators.py)
                    ↓
            Сохранение в БД (SQLAlchemy)
                    ↓
            Создание записи в audit_logs
                    ↓
            Уведомление в UI
            ✅ Спортсмен добавлен
```

---

## 🛠️ Технический стек

| Компонент | Технология | Версия |
|-----------|-----------|--------|
| **Веб-фреймворк** | Streamlit | 1.28.1 |
| **ORM** | SQLAlchemy | 2.0.23 |
| **БД (Dev)** | SQLite | 3.x |
| **БД (Prod)** | PostgreSQL | 13+ |
| **Визуализация** | Plotly | 5.18.0 |
| **Данные** | Pandas | 2.1.4 |
| **Хеширование** | bcrypt | 4.1.1 |
| **Python** | CPython | 3.10+ |

---

## 🚀 Развёртывание

### Локальное
```bash
streamlit run app.py
```

### Docker (опционально)
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

### Streamlit Cloud
- Push на GitHub
- Авторизация через Streamlit Cloud
- Автоматическое развёртывание

### Kubernetes (enterprise)
- Dockerfile
- Helm charts
- PostgreSQL StatefulSet

---

## 🔐 Безопасность

### Имплементировано
- ✅ Хеширование паролей (bcrypt)
- ✅ Session-based аутентификация
- ✅ RBAC матрица доступа
- ✅ Валидация входных данных
- ✅ Логирование всех действий
- ✅ Защита от SQL-инъекций (SQLAlchemy)

### Рекомендуется для production
- 🔒 HTTPS/TLS
- 🔒 Rate limiting
- 🔒 CORS политика
- 🔒 API keys для интеграций
- 🔒 Шифрование ПД в БД
- 🔒 Резервное копирование

---

## 📈 Масштабируемость

### Текущие ограничения
- SQLite: ~10,000 записей
- Single-threaded Streamlit
- In-memory session state

### Рекомендации для масштабирования
1. **PostgreSQL** вместо SQLite
2. **Redis** для кеширования
3. **Load balancer** (nginx)
4. **Celery** для async задач
5. **CDN** для статики

---

## 📝 Версионирование

### Текущая версия: 1.0
- ✅ Базовая аутентификация
- ✅ 30 спортсменов с мок-данными
- ✅ Графики результатов и мед. показателей
- ✅ RBAC система

### Планируемые улучшения (v1.1)
- 📌 Multi-language поддержка
- 📌 CSV/Excel экспорт
- 📌 Email уведомления
- 📌 Календарь соревнований

---

**Последнее обновление:** Ноябрь 2025
