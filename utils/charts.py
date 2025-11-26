"""
Утилиты для построения графиков и аналитики
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from database.connection import get_db_session
from database.models import CompetitionResult, MedicalData


def plot_competition_results_trend(athlete_id: int, event: str = None):
    """График динамики результатов соревнований"""
    session = get_db_session()
    
    results = session.query(CompetitionResult).filter(
        CompetitionResult.athlete_id == athlete_id
    ).order_by(CompetitionResult.competition_date).all()
    
    session.close()
    
    if not results:
        st.warning("Результатов соревнований не найдено")
        return
    
    df = pd.DataFrame([{
        'date': r.competition_date,
        'result': r.result,
        'competition': r.competition_name,
        'place': r.place
    } for r in results])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['result'],
        mode='lines+markers',
        name='Результат',
        line=dict(color='#667eea', width=2),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="📊 Динамика результатов (2 года)",
        xaxis_title="Дата",
        yaxis_title="Результат",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_vo2max_trend(athlete_id: int):
    """График МПК (VO2max) за время"""
    session = get_db_session()
    
    medical_data = session.query(MedicalData).filter(
        MedicalData.athlete_id == athlete_id
    ).order_by(MedicalData.measurement_date).all()
    
    session.close()
    
    if not medical_data:
        st.warning("Медицинских данных не найдено")
        return
    
    df = pd.DataFrame([{
        'date': m.measurement_date,
        'vo2max_abs': m.vo2max,
        'vo2max_rel': m.vo2max_relative
    } for m in medical_data if m.vo2max and m.vo2max_relative])
    
    if df.empty:
        st.warning("Данные МПК отсутствуют")
        return
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['vo2max_abs'],
        name='МПК абсолютный (мл/мин)',
        mode='lines+markers',
        line=dict(color='#28a745', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['vo2max_rel'],
        name='МПК относительный (мл/кг/мин)',
        mode='lines+markers',
        line=dict(color='#ffc107', width=2),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title="📈 Динамика МПК (VO2max)",
        xaxis_title="Дата",
        yaxis_title="МПК абсолютный (мл/мин)",
        yaxis2=dict(
            title="МПК относительный (мл/кг/мин)",
            overlaying='y',
            side='right'
        ),
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_heart_rate_zones(athlete_id: int):
    """График пульсовых зон"""
    session = get_db_session()
    
    medical = session.query(MedicalData).filter(
        MedicalData.athlete_id == athlete_id
    ).order_by(MedicalData.measurement_date.desc()).first()
    
    session.close()
    
    if not medical:
        st.warning("Пульсовые зоны не определены")
        return
    
    zones = [
        ("Зона 1 (Восстановление)", medical.zone_1_heart_rate, "#28a745"),
        ("Зона 2 (Аэробная)", medical.zone_2_heart_rate, "#ffc107"),
        ("Зона 3 (Пороговая)", medical.zone_3_heart_rate, "#fd7e14"),
        ("Зона 4 (Анаэробная)", medical.zone_4_heart_rate, "#dc3545"),
        ("Зона 5 (Максимальная)", medical.zone_5_heart_rate, "#c82333"),
    ]
    
    fig = go.Figure()
    
    for i, (zone_name, zone_range, color) in enumerate(zones):
        if zone_range:
            fig.add_trace(go.Bar(
                y=[zone_name],
                x=[int(zone_range.split('-')[1]) - int(zone_range.split('-')[0])],
                orientation='h',
                name=zone_name,
                marker_color=color,
                text=zone_range,
                textposition='inside',
                hovertemplate=f"{zone_name}: {zone_range} уд/мин<extra></extra>"
            ))
    
    fig.update_layout(
        title="🫀 Пульсовые зоны",
        xaxis_title="ЧСС (уд/мин)",
        showlegend=False,
        template='plotly_white',
        height=300,
        margin=dict(l=200)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_morphometry_trend(athlete_id: int):
    """График морфометрических показателей"""
    session = get_db_session()
    
    medical_data = session.query(MedicalData).filter(
        MedicalData.athlete_id == athlete_id
    ).order_by(MedicalData.measurement_date).all()
    
    session.close()
    
    df = pd.DataFrame([{
        'date': m.measurement_date,
        'weight': m.weight,
        'fat_pct': m.fat_percentage
    } for m in medical_data if m.weight and m.fat_percentage])
    
    if df.empty:
        st.warning("Морфометрические данные отсутствуют")
        return
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['weight'],
        name='Вес (кг)',
        mode='lines+markers',
        line=dict(color='#667eea', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['fat_pct'],
        name='% Жира',
        mode='lines+markers',
        line=dict(color='#dc3545', width=2),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title="⚖️ Морфометрические показатели",
        xaxis_title="Дата",
        yaxis_title="Вес (кг)",
        yaxis2=dict(
            title="% Жира",
            overlaying='y',
            side='right'
        ),
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_blood_markers(athlete_id: int):
    """График показателей крови"""
    session = get_db_session()
    
    medical_data = session.query(MedicalData).filter(
        MedicalData.athlete_id == athlete_id
    ).order_by(MedicalData.measurement_date).all()
    
    session.close()
    
    df = pd.DataFrame([{
        'date': m.measurement_date,
        'hemoglobin': m.hemoglobin,
        'hematocrit': m.hematocrit,
        'lactate': m.lactate
    } for m in medical_data])
    
    if df.empty:
        st.warning("Показатели крови отсутствуют")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        latest_hgb = df['hemoglobin'].iloc[-1] if not df.empty else None
        st.metric("🔴 Гемоглобин (г/дл)", f"{latest_hgb:.1f}", delta=None)
    
    with col2:
        latest_hct = df['hematocrit'].iloc[-1] if not df.empty else None
        st.metric("🩸 Гематокрит (%)", f"{latest_hct:.1f}", delta=None)
    
    with col3:
        latest_lac = df['lactate'].iloc[-1] if not df.empty else None
        st.metric("⚡ Лактат (ммоль/л)", f"{latest_lac:.1f}", delta=None)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['hemoglobin'],
        name='Гемоглобин',
        mode='lines+markers',
        line=dict(color='#dc3545', width=2)
    ))
    
    fig.update_layout(
        title="🧬 Гемоглобин (тренд)",
        xaxis_title="Дата",
        yaxis_title="г/дл",
        template='plotly_white',
        height=350
    )
    
    st.plotly_chart(fig, use_container_width=True)
