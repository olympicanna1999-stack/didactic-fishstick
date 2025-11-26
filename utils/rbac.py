import streamlit as st
from typing import List, Set


# Матрица доступа по ролям
ACCESS_MATRIX = {
    "admin": {
        "view_all_athletes": True,
        "view_all_results": True,
        "view_all_medical": True,
        "edit_athlete_profile": True,
        "edit_results": True,
        "edit_medical_data": True,
        "delete_data": True,
        "manage_users": True,
        "view_analytics": True,
        "export_data": True,
        "view_own_data_only": False
    },
    "curator": {
        "view_all_athletes": True,  # Только своего вида спорта
        "view_all_results": True,  # Только своего вида спорта
        "view_all_medical": True,  # Только своего вида спорта
        "edit_athlete_profile": True,
        "edit_results": True,
        "edit_medical_data": True,
        "delete_data": False,
        "manage_users": False,
        "view_analytics": True,
        "export_data": True,
        "view_own_data_only": False,
        "sports_restricted": True
    },
    "athlete": {
        "view_all_athletes": False,
        "view_all_results": False,
        "view_all_medical": False,
        "edit_athlete_profile": False,
        "edit_results": False,
        "edit_medical_data": False,
        "delete_data": False,
        "manage_users": False,
        "view_analytics": False,
        "export_data": False,
        "view_own_data_only": True
    }
}


def check_access(permission: str, user: dict | None = None) -> bool:
    """Проверка доступа пользователя к функции"""
    if user is None:
        user = st.session_state.get("user")
    
    if user is None:
        return False
    
    role = user.get("role", "athlete")
    if role not in ACCESS_MATRIX:
        return False
    
    return ACCESS_MATRIX[role].get(permission, False)


def get_user_sports(user_id: int) -> List[str]:
    """Получить виды спорта для куратора"""
    user = st.session_state.get("user")
    if user is None:
        return []
    
    if user.get("role") == "admin":
        return []  # Admin видит все виды спорта
    
    return user.get("sports", [])


def can_view_athlete(athlete_id: int, user: dict | None = None) -> bool:
    """Проверка доступа к профилю спортсмена"""
    if user is None:
        user = st.session_state.get("user")
    
    if user is None:
        return False
    
    role = user.get("role")
    
    if role == "admin":
        return True
    
    if role == "athlete":
        # Спортсмен может видеть только свой профиль
        return athlete_id == user.get("user_id")
    
    if role == "curator":
        # TODO: Проверить, что спортсмен в виде спорта куратора
        return True
    
    return False


def can_edit_athlete(athlete_id: int, user: dict | None = None) -> bool:
    """Проверка доступа к редактированию профиля"""
    if user is None:
        user = st.session_state.get("user")
    
    if user is None:
        return False
    
    role = user.get("role")
    
    if role == "admin":
        return True
    
    if role == "curator":
        # TODO: Проверить, что спортсмен в виде спорта куратора
        return True
    
    return False


def can_delete_data(user: dict | None = None) -> bool:
    """Проверка доступа к удалению данных"""
    if user is None:
        user = st.session_state.get("user")
    
    return user and user.get("role") == "admin"


def require_permission(permission: str):
    """Декоратор для проверки разрешений"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not check_access(permission):
                st.error(f"❌ У вас нет доступа: {permission}")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator
