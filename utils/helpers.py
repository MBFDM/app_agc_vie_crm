import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

def format_currency(value):
    """Formate un nombre en devise"""
    if value is None or pd.isna(value):
        return "0 €"
    return f"{value:,.2f} €".replace(",", " ")

def format_date(date_str):
    """Formate une date"""
    if pd.isna(date_str):
        return "Non définie"
    try:
        date = pd.to_datetime(date_str)
        return date.strftime("%d/%m/%Y")
    except:
        return str(date_str)

def get_status_color(status):
    """Retourne la couleur associée à un statut"""
    colors = {
        'Nouveau': '#667eea',
        'En contact': '#f6ad55',
        'Qualifié': '#38a169',
        'En cours': '#f6ad55',
        'À relancer': '#e53e3e',
        'Chaud': '#f093fb',
        'Confirmé': '#38a169',
        'Planifié': '#4299e1',
        'Passé': '#a0aec0'
    }
    return colors.get(status, '#718096')

def filter_by_date_range(df, date_column, days=30):
    """Filtre un DataFrame par plage de dates"""
    if df is None or df.empty:
        return df
    
    cutoff_date = datetime.now() - timedelta(days=days)
    df[date_column] = pd.to_datetime(df[date_column])
    return df[df[date_column] >= cutoff_date]

def get_kpi_metric(value, delta=None):
    """Retourne une métrique KPI formatée"""
    if delta:
        return f"{value} ({delta:+.1f}%)"
    return str(value)

def export_to_csv(df, filename):
    """Exporte un DataFrame en CSV"""
    if df is not None and not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"📥 Exporter {filename}",
            data=csv,
            file_name=f"{filename}.csv",
            mime="text/csv",
        )