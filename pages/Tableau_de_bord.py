import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import db
from utils.charts import *
from utils.helpers import *

st.set_page_config(page_title="Tableau de bord", page_icon="📊", layout="wide")

# CSS personnalisé
st.markdown("""
<style>
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #2d3748;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-trend {
        font-size: 0.9rem;
        color: #38a169;
    }
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# En-tête
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<h1 style="color: #2d3748;">📊 Tableau de bord analytique</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="color: #718096;">Dernière mise à jour : {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>', unsafe_allow_html=True)

with col2:
    if st.button("🔄 Actualiser les données", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Récupération des données
with st.spinner("Chargement des données..."):
    stats = db.get_dashboard_stats()
    leads_df = db.get_leads()
    prospects_df = db.get_prospects()
    customers_df = db.get_customers()
    appointments_df = db.get_appointments()

# KPIs principaux
st.markdown("### 📈 Indicateurs clés")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">Total Leads</div>
        <div class="metric-value">{stats['total_leads']}</div>
        <div class="metric-trend">↗️ +{stats.get('leads_growth', 0)}% vs mois dernier</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-container" style="border-left-color: #f093fb;">
        <div class="metric-label">Prospects actifs</div>
        <div class="metric-value">{stats['total_prospects']}</div>
        <div class="metric-trend">{stats.get('prospects_to_follow', 0)} à relancer</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-container" style="border-left-color: #43e97b;">
        <div class="metric-label">Clients</div>
        <div class="metric-value">{stats['total_customers']}</div>
        <div class="metric-trend">💰 {format_currency(stats.get('total_revenue', 0))}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-container" style="border-left-color: #4facfe;">
        <div class="metric-label">Taux conversion</div>
        <div class="metric-value">{stats['conversion_rate']}%</div>
        <div class="metric-trend">🎯 Objectif: 25%</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-container" style="border-left-color: #fa709a;">
        <div class="metric-label">RDV aujourd'hui</div>
        <div class="metric-value">{stats['today_appointments']}</div>
        <div class="metric-trend">📅 {stats.get('upcoming_appointments', 0)} cette semaine</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Graphiques principaux
col1, col2 = st.columns(2)

with col1:
    with st.container():
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 🎯 Répartition des leads par statut")
        
        leads_status = db.get_leads_by_status()
        if leads_status is not None and not leads_status.empty:
            fig = create_status_pie_chart(leads_status)
            st.plotly_chart(fig, use_container_width=True)
            
            # Ajouter un tableau récapitulatif
            total = leads_status['count'].sum()
            for _, row in leads_status.iterrows():
                percentage = (row['count'] / total * 100)
                st.markdown(f"- **{row['status']}**: {row['count']} ({percentage:.1f}%)")
        else:
            st.info("Aucune donnée disponible")
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    with st.container():
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("#### 🔥 Répartition des prospects")
        
        prospects_status = db.get_prospects_by_status()
        if prospects_status is not None and not prospects_status.empty:
            fig = px.bar(
                prospects_status,
                x='status',
                y='count',
                color='status',
                title="",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Nombre")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune donnée disponible")
        st.markdown('</div>', unsafe_allow_html=True)

# Évolution temporelle
with st.container():
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("#### 📈 Évolution mensuelle")
    
    trends = db.get_monthly_trends()
    if trends is not None and not trends.empty:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=trends['month'],
            y=trends['leads_count'],
            mode='lines+markers',
            name='Leads',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=trends['month'],
            y=trends['customers_count'],
            mode='lines+markers',
            name='Clients',
            line=dict(color='#43e97b', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            xaxis_title="",
            yaxis_title="Nombre",
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée d'évolution disponible")
    st.markdown('</div>', unsafe_allow_html=True)

# Tableaux récapitulatifs
st.markdown("### 📋 Aperçu rapide")

tab1, tab2, tab3 = st.tabs(["🆕 Derniers leads", "🎯 Prochains RDV", "🤝 Nouveaux clients"])

with tab1:
    if leads_df is not None and not leads_df.empty:
        recent_leads = leads_df.head(10).copy()
        recent_leads['created_at'] = pd.to_datetime(recent_leads['created_at']).dt.strftime('%d/%m/%Y')
        recent_leads['intérêt'] = recent_leads['interest_level'].apply(lambda x: "⭐" * x)
        
        st.dataframe(
            recent_leads[['name', 'company', 'status', 'intérêt', 'created_at']],
            use_container_width=True,
            hide_index=True,
            column_config={
                'name': 'Nom',
                'company': 'Entreprise',
                'status': 'Statut',
                'intérêt': 'Niveau',
                'created_at': 'Date'
            }
        )
    else:
        st.info("Aucun lead récent")

with tab2:
    upcoming = db.get_upcoming_appointments(7)
    if upcoming is not None and not upcoming.empty:
        upcoming['date'] = pd.to_datetime(upcoming['appointment_date']).dt.strftime('%d/%m/%Y %H:%M')
        upcoming['dans'] = (pd.to_datetime(upcoming['appointment_date']) - datetime.now()).dt.days
        upcoming['dans'] = upcoming['dans'].apply(lambda x: "Aujourd'hui" if x == 0 else f"J-{x}" if x > 0 else "Passé")
        
        st.dataframe(
            upcoming[['title', 'customer_name', 'date', 'dans', 'status']],
            use_container_width=True,
            hide_index=True,
            column_config={
                'title': 'Titre',
                'customer_name': 'Client',
                'date': 'Date',
                'dans': 'Échéance',
                'status': 'Statut'
            }
        )
    else:
        st.info("Aucun rendez-vous à venir")

with tab3:
    if customers_df is not None and not customers_df.empty:
        recent_customers = customers_df.head(10).copy()
        recent_customers['created_at'] = pd.to_datetime(recent_customers['created_at']).dt.strftime('%d/%m/%Y')
        recent_customers['ca'] = recent_customers['revenue'].apply(format_currency)
        
        st.dataframe(
            recent_customers[['name', 'company', 'industry', 'ca', 'created_at']],
            use_container_width=True,
            hide_index=True,
            column_config={
                'name': 'Nom',
                'company': 'Entreprise',
                'industry': 'Secteur',
                'ca': "Chiffre d'affaires",
                'created_at': 'Date'
            }
        )
    else:
        st.info("Aucun client récent")

# Section d'export
st.markdown("---")
with st.expander("📥 Exporter les rapports"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Rapport complet (PDF)", use_container_width=True):
            st.info("Fonctionnalité à venir")
    
    with col2:
        if st.button("📈 Export Excel", use_container_width=True):
            st.info("Fonctionnalité à venir")
    
    with col3:
        if st.button("📧 Envoyer par email", use_container_width=True):
            st.info("Fonctionnalité à venir")