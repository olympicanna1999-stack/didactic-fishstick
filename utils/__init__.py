"""
Модуль утилит для работы с базой данных, аутентификацией и графиками
Цифровой реестр олимпийского резерва
"""

__version__ = '1.0.0'
__author__ = 'Olympic Reserve Development Team'
__description__ = 'Utils package for Olympic Reserve Registry system'

# Явно импортируем модули пакета для удобства
try:
    from .auth import (
        check_authentication,
        get_current_user,
        logout_user,
        authenticate_user,
        hash_password,
        verify_password
    )
except ImportError as e:
    print(f"Warning: Could not import auth: {e}")

try:
    from .database import (
        get_db_connection,
        init_database,
        execute_query,
        get_athletes,
        get_athlete_by_id,
        get_sport_results,
        add_sport_result,
        get_medical_data,
        get_functional_tests,
        get_development_plans,
        get_documents,
        get_sports,
        get_regions,
        get_athlete_statistics,
        get_sport_statistics
    )
except ImportError as e:
    print(f"Warning: Could not import database: {e}")

try:
    from .charts import (
        plot_results_dynamics,
        plot_vo2max_dynamics,
        plot_medical_indicators,
        plot_anthropometry,
        plot_heart_rate_zones,
        plot_places_distribution,
        plot_competition_frequency,
        plot_functional_profile
    )
except ImportError as e:
    print(f"Warning: Could not import charts: {e}")

__all__ = [
    'check_authentication',
    'get_current_user',
    'logout_user',
    'authenticate_user',
    'hash_password',
    'verify_password',
    'get_db_connection',
    'init_database',
    'execute_query',
    'get_athletes',
    'get_athlete_by_id',
    'get_sport_results',
    'add_sport_result',
    'get_medical_data',
    'get_functional_tests',
    'get_development_plans',
    'get_documents',
    'get_sports',
    'get_regions',
    'get_athlete_statistics',
    'get_sport_statistics',
    'plot_results_dynamics',
    'plot_vo2max_dynamics',
    'plot_medical_indicators',
    'plot_anthropometry',
    'plot_heart_rate_zones',
    'plot_places_distribution',
    'plot_competition_frequency',
    'plot_functional_profile'
]
