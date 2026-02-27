import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def create_status_pie_chart(data, title="Répartition par statut"):
    """Crée un graphique en camembert pour la répartition par statut"""
    if data is None or data.empty:
        return None
    
    fig = px.pie(
        data, 
        values='count', 
        names='status',
        title=title,
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.4
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False)
    return fig

def create_bar_chart(data, x_col, y_col, title, color=None):
    """Crée un graphique en barres"""
    if data is None or data.empty:
        return None
    
    fig = px.bar(
        data,
        x=x_col,
        y=y_col,
        title=title,
        color=color if color else x_col,
        color_continuous_scale='Viridis'
    )
    fig.update_layout(xaxis_title="", yaxis_title="")
    return fig

def create_trend_line_chart(data, x_col, y_cols, title):
    """Crée un graphique de tendance"""
    if data is None or data.empty:
        return None
    
    fig = go.Figure()
    
    for y_col in y_cols:
        fig.add_trace(go.Scatter(
            x=data[x_col],
            y=data[y_col],
            mode='lines+markers',
            name=y_col.replace('_', ' ').title(),
            line=dict(width=3)
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="",
        yaxis_title="Nombre",
        hovermode='x unified'
    )
    return fig

def create_gauge_chart(value, title, min_value=0, max_value=100):
    """Crée un graphique de type jauge"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [min_value, max_value]},
            'bar': {'color': "#667eea"},
            'steps': [
                {'range': [0, 50], 'color': "#f093fb"},
                {'range': [50, 80], 'color': "#43e97b"},
                {'range': [80, 100], 'color': "#4facfe"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(height=200)
    return fig

def create_timeline_chart(appointments_df):
    """Crée une timeline des rendez-vous"""
    if appointments_df is None or appointments_df.empty:
        return None
    
    fig = px.timeline(
        appointments_df,
        x_start="appointment_date",
        x_end=appointments_df["appointment_date"] + pd.to_timedelta(appointments_df["duration"], unit='m'),
        y="title",
        color="status",
        title="Calendrier des rendez-vous",
        color_discrete_map={
            'Confirmé': '#38a169',
            'Planifié': '#4299e1',
            'Passé': '#a0aec0'
        }
    )
    
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(xaxis_title="Date", yaxis_title="")
    return fig