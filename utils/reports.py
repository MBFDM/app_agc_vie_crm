import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import plotly.graph_objects as go
from io import BytesIO

class ReportGenerator:
    """Générateur de rapports pour le CRM"""
    
    @staticmethod
    def generate_daily_report(leads_df, prospects_df, customers_df, appointments_df):
        """Génère un rapport quotidien"""
        today = datetime.now().date()
        
        report = {
            'date': today.strftime('%d/%m/%Y'),
            'indicateurs': {
                'nouveaux_leads': len(leads_df[pd.to_datetime(leads_df['created_at']).dt.date == today]) if leads_df is not None else 0,
                'prospects_relance': len(prospects_df[pd.to_datetime(prospects_df['next_follow_up']).dt.date == today]) if prospects_df is not None else 0,
                'nouveaux_clients': len(customers_df[pd.to_datetime(customers_df['created_at']).dt.date == today]) if customers_df is not None else 0,
                'rdv_aujourdhui': len(appointments_df[pd.to_datetime(appointments_df['appointment_date']).dt.date == today]) if appointments_df is not None else 0
            },
            'top_actions': []
        }
        
        return report
    
    @staticmethod
    def generate_weekly_report(leads_df, prospects_df, customers_df):
        """Génère un rapport hebdomadaire"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        if leads_df is not None:
            leads_df['created_at'] = pd.to_datetime(leads_df['created_at'])
            weekly_leads = leads_df[
                (leads_df['created_at'] >= start_date) &
                (leads_df['created_at'] <= end_date)
            ]
        else:
            weekly_leads = pd.DataFrame()
        
        if customers_df is not None:
            customers_df['created_at'] = pd.to_datetime(customers_df['created_at'])
            weekly_customers = customers_df[
                (customers_df['created_at'] >= start_date) &
                (customers_df['created_at'] <= end_date)
            ]
        else:
            weekly_customers = pd.DataFrame()
        
        report = {
            'periode': f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}",
            'stats': {
                'leads_nouveaux': len(weekly_leads),
                'clients_nouveaux': len(weekly_customers),
                'evolution_leads': ReportGenerator._calculate_growth(leads_df, 7) if leads_df is not None else 0,
                'evolution_clients': ReportGenerator._calculate_growth(customers_df, 7) if customers_df is not None else 0
            }
        }
        
        return report
    
    @staticmethod
    def generate_monthly_report(leads_df, prospects_df, customers_df):
        """Génère un rapport mensuel"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        report = ReportGenerator.generate_weekly_report(leads_df, prospects_df, customers_df)
        report['periode'] = f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"
        
        # Ajout d'analyses mensuelles
        if customers_df is not None:
            monthly_revenue = customers_df['revenue'].sum() if 'revenue' in customers_df.columns else 0
            report['stats']['ca_mensuel'] = monthly_revenue
        
        return report
    
    @staticmethod
    def _calculate_growth(df, days):
        """Calcule la croissance sur une période"""
        if df is None or df.empty:
            return 0
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        previous_start = start_date - timedelta(days=days)
        
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        current_period = len(df[
            (df['created_at'] >= start_date) &
            (df['created_at'] <= end_date)
        ])
        
        previous_period = len(df[
            (df['created_at'] >= previous_start) &
            (df['created_at'] < start_date)
        ])
        
        if previous_period > 0:
            growth = ((current_period - previous_period) / previous_period) * 100
        else:
            growth = 100 if current_period > 0 else 0
        
        return round(growth, 1)
    
    @staticmethod
    def export_to_excel(dataframes_dict):
        """Exporte plusieurs DataFrames vers un fichier Excel"""
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for sheet_name, df in dataframes_dict.items():
                if df is not None and not df.empty:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        output.seek(0)
        return output
    
    @staticmethod
    def create_performance_chart(leads_df, customers_df):
        """Crée un graphique de performance comparatif"""
        if leads_df is None or customers_df is None:
            return None
        
        leads_df['created_at'] = pd.to_datetime(leads_df['created_at'])
        customers_df['created_at'] = pd.to_datetime(customers_df['created_at'])
        
        # Agrégation par mois
        leads_monthly = leads_df.groupby(leads_df['created_at'].dt.to_period('M')).size()
        customers_monthly = customers_df.groupby(customers_df['created_at'].dt.to_period('M')).size()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=leads_monthly.index.astype(str),
            y=leads_monthly.values,
            mode='lines+markers',
            name='Leads',
            line=dict(color='#667eea', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=customers_monthly.index.astype(str),
            y=customers_monthly.values,
            mode='lines+markers',
            name='Clients',
            line=dict(color='#43e97b', width=3)
        ))
        
        fig.update_layout(
            title="Performance mensuelle",
            xaxis_title="Mois",
            yaxis_title="Nombre",
            hovermode='x unified'
        )
        
        return fig