import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
import streamlit as st

class CRMAnalytics:
    """Classe pour les analyses avancées du CRM"""
    
    @staticmethod
    def predict_future_trends(df, date_col, value_col, periods=6):
        """Prédit les tendances futures"""
        if df is None or df.empty:
            return None
        
        # Préparation des données
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col)
        
        # Création des features temporelles
        df['days'] = (df[date_col] - df[date_col].min()).dt.days
        
        # Modèle de régression linéaire
        X = df['days'].values.reshape(-1, 1)
        y = df[value_col].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Prédictions futures
        last_day = df['days'].max()
        future_days = np.array([last_day + i * 30 for i in range(1, periods + 1)]).reshape(-1, 1)
        predictions = model.predict(future_days)
        
        return predictions
    
    @staticmethod
    def calculate_conversion_funnel(leads_df, prospects_df, customers_df):
        """Calcule l'entonnoir de conversion"""
        funnel = {
            'étape': ['Leads', 'Prospects qualifiés', 'Clients'],
            'nombre': [
                len(leads_df) if leads_df is not None else 0,
                len(prospects_df[prospects_df['status'] == 'Chaud']) if prospects_df is not None else 0,
                len(customers_df) if customers_df is not None else 0
            ]
        }
        
        df = pd.DataFrame(funnel)
        
        # Calcul des taux de conversion
        if df.loc[0, 'nombre'] > 0:
            df['taux_conversion'] = [
                100,
                (df.loc[1, 'nombre'] / df.loc[0, 'nombre'] * 100),
                (df.loc[2, 'nombre'] / df.loc[0, 'nombre'] * 100)
            ]
        else:
            df['taux_conversion'] = [0, 0, 0]
        
        return df
    
    @staticmethod
    def analyze_sales_cycle(customers_df):
        """Analyse le cycle de vente moyen"""
        if customers_df is None or customers_df.empty:
            return None
        
        # Simulation de données de cycle de vente
        # Dans un cas réel, vous auriez une colonne 'date_deal_closed'
        np.random.seed(42)
        cycles = np.random.normal(45, 15, len(customers_df))
        cycles = np.clip(cycles, 15, 90)
        
        return {
            'moyenne': np.mean(cycles),
            'médiane': np.median(cycles),
            'min': np.min(cycles),
            'max': np.max(cycles),
            'ecart_type': np.std(cycles)
        }
    
    @staticmethod
    def customer_lifetime_value(customers_df, years=3):
        """Calcule la valeur vie client projetée"""
        if customers_df is None or customers_df.empty:
            return None
        
        customers_df = customers_df.copy()
        customers_df['revenue'] = pd.to_numeric(customers_df['revenue'], errors='coerce')
        
        # Filtre les clients avec CA valide
        valid_clients = customers_df[customers_df['revenue'].notna()]
        
        if valid_clients.empty:
            return None
        
        # Calcul du CLV simple (CA annuel * années)
        valid_clients['clv'] = valid_clients['revenue'] * years
        
        return valid_clients[['name', 'company', 'revenue', 'clv']].sort_values('clv', ascending=False)
    
    @staticmethod
    def create_heatmap(prospects_df):
        """Crée une heatmap des activités de relance"""
        if prospects_df is None or prospects_df.empty:
            return None
        
        prospects_df = prospects_df.copy()
        prospects_df['next_follow_up'] = pd.to_datetime(prospects_df['next_follow_up'])
        
        # Extraction du jour de la semaine et de l'heure
        prospects_df['jour'] = prospects_df['next_follow_up'].dt.day_name()
        prospects_df['semaine'] = prospects_df['next_follow_up'].dt.isocalendar().week
        
        # Création de la matrice de heatmap
        heatmap_data = prospects_df.groupby(['jour', 'semaine']).size().reset_index(name='count')
        
        # Ordre des jours
        jour_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        jours_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        jour_mapping = dict(zip(jour_order, jours_fr))
        
        heatmap_data['jour_fr'] = heatmap_data['jour'].map(jour_mapping)
        
        return heatmap_data
    
    @staticmethod
    def segment_customers(customers_df):
        """Segmente les clients par valeur"""
        if customers_df is None or customers_df.empty:
            return None
        
        customers_df = customers_df.copy()
        customers_df['revenue'] = pd.to_numeric(customers_df['revenue'], errors='coerce')
        
        # Définition des seuils
        revenue_valid = customers_df['revenue'].dropna()
        if revenue_valid.empty:
            return None
        
        q1 = revenue_valid.quantile(0.25)
        q3 = revenue_valid.quantile(0.75)
        
        def segment_client(revenue):
            if pd.isna(revenue):
                return 'Non défini'
            elif revenue >= q3:
                return '💰 Grand compte'
            elif revenue >= q1:
                return '📊 Client moyen'
            else:
                return '💼 Petit compte'
        
        customers_df['segment'] = customers_df['revenue'].apply(segment_client)
        
        return customers_df