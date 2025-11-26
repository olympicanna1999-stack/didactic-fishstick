"""
Модуль профиля спортсмена с аналитикой
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from utils.database import get_athlete_by_id, get_sport_results

def show_athlete_profile(athlete_id: int):
    """Показывает полный профиль спортсмена с аналитикой"""
    
    # Получаем данные спортсмена
    athlete = get_athlete_by_id(athlete_id)
    
    if athlete.empty:
        st.error("❌ Спортсмен не найден")
        return
    
    athlete_data = athlete.iloc[0]
    
    # Заголовок
    st.title(f"👤 {athlete_data['first_name']} {athlete_data['last_name']}")
    
    # Информация спортсмена
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🆔 ID", athlete_data['id'])
    with col2:
        st.metric("⚧ Пол", "Мужской" if athlete_data['gender'] == 'М' else "Женский")
    with col3:
        birth_date = pd.to_datetime(athlete_data['birth_date'])
        age = (datetime.now() - birth_date).days // 365
        st.metric("🎂 Возраст", f"{age} лет")
    with col4:
        st.metric("📅 Дата рождения", athlete_data['birth_date'])
    with col5:
        status_emoji = "✅" if athlete_data['program_status'] == 'active' else "⏸"
        st.metric("🏅 Статус", athlete_data['program_status'], delta=status_emoji)
    
    st.markdown("---")
    
    # Получаем результаты соревнований
    results = get_sport_results(athlete_id=athlete_id, limit=100)
    
    # Вкладки
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Статистика", "🏆 Результаты", "📈 Динамика", "🎯 Анализ"])
    
    with tab1:
        show_athlete_statistics(athlete_id, results)
    
    with tab2:
        show_athlete_results(results)
    
    with tab3:
        show_athlete_dynamics(athlete_id, results)
    
    with tab4:
        show_athlete_analysis(athlete_id, results)

def show_athlete_statistics(athlete_id: int, results: pd.DataFrame):
    """Статистика спортсмена"""
    st.subheader("📊 Основная статистика")
    
    if results.empty:
        st.info("📭 Нет данных о соревнованиях")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Всего соревнований
    total_competitions = len(results)
    with col1:
        st.metric("🏆 Всего соревнований", total_competitions)
    
    # Средний результат (место)
    avg_place = results['place'].mean() if 'place' in results.columns else 0
    with col2:
        st.metric("📍 Среднее место", f"{avg_place:.1f}")
    
    # Лучший результат
    best_place = results['place'].min() if 'place' in results.columns else 0
    with col3:
        st.metric("🥇 Лучший результат", f"{int(best_place)} место")
    
    # Последний результат
    if not results.empty:
        last_date = results['competition_date'].max()
        last_place = results[results['competition_date'] == last_date]['place'].values[0] if 'place' in results.columns else 0
        with col4:
            st.metric("⚡ Последний результат", f"{int(last_place)} место")
    
    st.markdown("---")
    
    # Распределение мест
    st.subheader("Распределение мест на соревнованиях")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'place' in results.columns:
            place_counts = results['place'].value_counts().sort_index().head(10)
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(place_counts.index, place_counts.values, color='#3498DB', edgecolor='black', linewidth=1.5)
            ax.set_xlabel("Место", fontsize=12, fontweight='bold')
            ax.set_ylabel("Количество", fontsize=12, fontweight='bold')
            ax.set_title("Распределение мест", fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            st.pyplot(fig)
    
    with col2:
        if 'competition_name' in results.columns:
            comp_counts = results['competition_name'].value_counts()
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = plt.cm.Set3(np.linspace(0, 1, len(comp_counts)))
            ax.pie(comp_counts, labels=comp_counts.index, autopct='%1.1f%%', colors=colors, startangle=90)
            ax.set_title("Участие в соревнованиях", fontsize=14, fontweight='bold')
            st.pyplot(fig)

def show_athlete_results(results: pd.DataFrame):
    """Таблица результатов"""
    st.subheader("🏆 Все результаты")
    
    if results.empty:
        st.info("📭 Нет результатов")
        return
    
    # Фильтры
    col1, col2 = st.columns(2)
    
    with col1:
        if 'competition_name' in results.columns:
            comp_filter = st.multiselect(
                "Фильтр по соревнованию:",
                results['competition_name'].unique(),
                default=results['competition_name'].unique()[:3]
            )
    
    with col2:
        if 'discipline' in results.columns:
            disc_filter = st.multiselect(
                "Фильтр по дисциплине:",
                results['discipline'].unique(),
                default=results['discipline'].unique()
            )
    
    # Применяем фильтры
    filtered = results
    if comp_filter:
        filtered = filtered[filtered['competition_name'].isin(comp_filter)]
    if disc_filter:
        filtered = filtered[filtered['discipline'].isin(disc_filter)]
    
    # Сортировка по дате (новые первыми)
    if 'competition_date' in filtered.columns:
        filtered = filtered.sort_values('competition_date', ascending=False)
    
    # Отображение
    display_data = filtered[['competition_date', 'competition_name', 'discipline', 'result', 'place']].copy()
    display_data.columns = ['Дата', 'Соревнование', 'Дисциплина', 'Результат', 'Место']
    
    st.dataframe(display_data, use_container_width=True, hide_index=True)
    
    st.info(f"📋 Всего результатов: {len(filtered)}")

def show_athlete_dynamics(athlete_id: int, results: pd.DataFrame):
    """Динамика результатов за год"""
    st.subheader("📈 Динамика результатов за год")
    
    if results.empty:
        st.info("📭 Нет данных для анализа динамики")
        return
    
    # Сортируем по дате
    if 'competition_date' in results.columns:
        results_sorted = results.sort_values('competition_date')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Динамика мест
            if 'place' in results.columns and 'competition_date' in results.columns:
                fig, ax = plt.subplots(figsize=(12, 6))
                
                dates = pd.to_datetime(results_sorted['competition_date'])
                places = results_sorted['place'].values
                
                ax.plot(dates, places, marker='o', linewidth=2.5, markersize=8, 
                       color='#E74C3C', markerfacecolor='#C0392B', markeredgewidth=2)
                ax.invert_yaxis()  # Инвертируем ось (1 место вверху)
                ax.fill_between(dates, places, alpha=0.2, color='#E74C3C')
                
                ax.set_xlabel("Дата", fontsize=12, fontweight='bold')
                ax.set_ylabel("Место", fontsize=12, fontweight='bold')
                ax.set_title("Динамика мест за год", fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3)
                
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
        
        with col2:
            # Тренд улучшения/ухудшения
            if 'place' in results.columns:
                fig, ax = plt.subplots(figsize=(12, 6))
                
                # Скользящее среднее
                places = results_sorted['place'].values
                window = min(3, len(places))
                moving_avg = pd.Series(places).rolling(window=window, center=True).mean()
                
                dates = pd.to_datetime(results_sorted['competition_date'])
                
                ax.plot(dates, places, marker='o', label='Результаты', 
                       linewidth=1.5, markersize=6, color='#3498DB', alpha=0.6)
                ax.plot(dates, moving_avg, label='Тренд', 
                       linewidth=3, color='#2ECC71', marker='s', markersize=8)
                
                ax.invert_yaxis()
                ax.set_xlabel("Дата", fontsize=12, fontweight='bold')
                ax.set_ylabel("Место", fontsize=12, fontweight='bold')
                ax.set_title("Тренд результатов", fontsize=14, fontweight='bold')
                ax.legend(loc='best', fontsize=11)
                ax.grid(True, alpha=0.3)
                
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
        
        st.markdown("---")
        
        # Статистика по месяцам
        st.subheader("📊 Анализ по месяцам")
        
        results_sorted['month'] = pd.to_datetime(results_sorted['competition_date']).dt.to_period('M')
        monthly_stats = results_sorted.groupby('month').agg({
            'place': ['count', 'mean', 'min']
        }).round(2)
        
        monthly_stats.columns = ['Соревнований', 'Среднее место', 'Лучший результат']
        
        st.dataframe(monthly_stats, use_container_width=True)

def show_athlete_analysis(athlete_id: int, results: pd.DataFrame):
    """Анализ и прогноз"""
    st.subheader("🎯 Детальный анализ")
    
    if results.empty:
        st.info("📭 Недостаточно данных для анализа")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Тренд
        if 'place' in results.columns:
            places = results['place'].values
            if len(places) > 1:
                trend = places[-1] - places[0]
                if trend < 0:
                    st.success(f"📈 Улучшение на {abs(int(trend))} мест")
                elif trend > 0:
                    st.warning(f"📉 Ухудшение на {int(trend)} мест")
                else:
                    st.info("➡️ Стабильный результат")
    
    with col2:
        # Консистентность
        if 'place' in results.columns:
            places = results['place'].values
            std_dev = np.std(places)
            st.metric("🎯 Консистентность", f"{std_dev:.2f}", 
                     delta="Ниже лучше", delta_color="inverse")
    
    with col3:
        # Активность
        last_30_days = results[
            pd.to_datetime(results['competition_date']) >= 
            datetime.now() - timedelta(days=30)
        ]
        st.metric("⚡ Соревнований за 30 дней", len(last_30_days))
    
    st.markdown("---")
    
    # Производительность по дисциплинам
    if 'discipline' in results.columns and 'place' in results.columns:
        st.subheader("🏃 Производительность по дисциплинам")
        
        discipline_stats = results.groupby('discipline').agg({
            'place': ['count', 'mean', 'min', 'max']
        }).round(2)
        
        discipline_stats.columns = ['Участий', 'Среднее место', 'Лучший результат', 'Худший результат']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.dataframe(discipline_stats, use_container_width=True)
        
        with col2:
            # Диаграмма
            discipline_avg = results.groupby('discipline')['place'].mean().sort_values()
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = ['#2ECC71' if x < 3 else '#3498DB' if x < 5 else '#E74C3C' for x in discipline_avg.values]
            ax.barh(discipline_avg.index, discipline_avg.values, color=colors, edgecolor='black', linewidth=1.5)
            ax.set_xlabel("Среднее место", fontsize=12, fontweight='bold')
            ax.set_title("Производительность по дисциплинам", fontsize=14, fontweight='bold')
            ax.invert_yaxis()
            st.pyplot(fig)
    
    st.markdown("---")
    
    # Рекомендации
    st.subheader("💡 Рекомендации")
    
    if not results.empty and 'place' in results.columns:
        places = results['place'].values
        avg_place = places.mean()
        
        recommendations = []
        
        if avg_place > 5:
            recommendations.append("⚠️ Среднее место выше 5 - нужна интенсивная подготовка")
        
        if len(places) < 3:
            recommendations.append("📊 Мало данных для анализа - необходимо больше соревнований")
        
        if places[-1] > places[0]:
            recommendations.append("📉 Тренд отрицательный - требуется коррекция программы подготовки")
        elif places[-1] < places[0]:
            recommendations.append("📈 Позитивный тренд - продолжать текущий режим подготовки")
        
        if not recommendations:
            recommendations.append("✅ Спортсмен показывает стабильные результаты")
        
        for rec in recommendations:
            st.info(rec)
