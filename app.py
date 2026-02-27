import streamlit as st
import pandas as pd
from datetime import datetime
from database import db
from utils.charts import *
from utils.helpers import *
import plotly.express as px

# Configuration de la page
st.set_page_config(
    page_title="AGC-VIE CRM Dashboard",
    page_icon="assets/logo.jpg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .stat-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("assets/logo.jpg", use_container_width =True)
    st.markdown("---")
    
    # Menu de navigation
    from streamlit_option_menu import option_menu
    with st.container():
        selected = option_menu(
            menu_title="Navigation",
            options=["Tableau de bord", "Leads", "Prospects", "Clients", "Rendez-vous"],
            icons=["bar-chart", "people", "bullseye", "person-lines-fill", "calendar"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#667eea", "font-size": "20px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px"},
                "nav-link-selected": {"background-color": "#667eea"},
            }
        )
    
    st.markdown("---")
    
    # Filtres globaux
    st.subheader("📅 Filtres")
    date_range = st.selectbox(
        "Période",
        ["7 derniers jours", "30 derniers jours", "90 derniers jours", "Tous"],
        index=1
    )
    
    # Sélection utilisateur
    users_df = db.get_users()
    if users_df is not None and not users_df.empty:
        user_list = ["Tous les utilisateurs"] + users_df['name'].tolist()
        selected_user = st.selectbox("👤 Utilisateur", user_list)
    else:
        selected_user = "Tous les utilisateurs"
    
    st.markdown("---")
    
    # Bouton de rafraîchissement
    if st.button("🔄 Rafraîchir les données"):
        st.cache_data.clear()
        st.rerun()

# Routeur de pages
if selected == "Tableau de bord":
    # Page Tableau de bord
    st.markdown('<p class="main-header">📊 Tableau de bord</p>', unsafe_allow_html=True)
    
    # Statistiques globales
    stats = db.get_dashboard_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Leads</div>
            <div class="metric-value">{stats['total_leads']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="metric-label">Prospects Actifs</div>
            <div class="metric-value">{stats['total_prospects']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <div class="metric-label">Clients</div>
            <div class="metric-value">{stats['total_customers']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <div class="metric-label">RDV Aujourd\'hui</div>
            <div class="metric-value">{stats['today_appointments']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        # Répartition des leads
        leads_status = db.get_leads_by_status()
        if leads_status is not None and not leads_status.empty:
            fig = create_status_pie_chart(leads_status, "Répartition des Leads")
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Répartition des prospects
        prospects_status = db.get_prospects_by_status()
        if prospects_status is not None and not prospects_status.empty:
            fig = create_status_pie_chart(prospects_status, "Répartition des Prospects")
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    # Tendance mensuelle
    trends = db.get_monthly_trends()
    if trends is not None and not trends.empty:
        fig = create_trend_line_chart(
            trends, 
            'month', 
            ['leads_count', 'customers_count'],
            "Évolution mensuelle"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Prochains rendez-vous
    st.subheader("📅 Prochains rendez-vous")
    upcoming = db.get_upcoming_appointments(7)
    if upcoming is not None and not upcoming.empty:
        upcoming['date_formatted'] = pd.to_datetime(upcoming['appointment_date']).dt.strftime('%d/%m/%Y %H:%M')
        st.dataframe(
            upcoming[['title', 'customer_name', 'date_formatted', 'status', 'user_name']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Aucun rendez-vous à venir")

elif selected == "Leads":
    # Page Leads
    st.markdown('<p class="main-header">👥 Gestion des Leads</p>', unsafe_allow_html=True)
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.multiselect(
            "Statut",
            ["Nouveau", "En contact", "Qualifié"],
            default=["Nouveau", "En contact"]
        )
    
    # Récupération des données
    user_id = None if selected_user == "Tous les utilisateurs" else users_df[users_df['name'] == selected_user]['id'].iloc[0]
    leads_df = db.get_leads(user_id)
    
    if leads_df is not None and not leads_df.empty:
        # Application des filtres
        if status_filter:
            leads_df = leads_df[leads_df['status'].isin(status_filter)]
        
        # Statistiques
        total_leads = len(leads_df)
        qualified = len(leads_df[leads_df['status'] == 'Qualifié'])
        conversion_rate = round((qualified / total_leads * 100) if total_leads > 0 else 0, 1)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total", total_leads)
        col2.metric("Qualifiés", qualified)
        col3.metric("Taux conversion", f"{conversion_rate}%")
        
        # Tableau des leads
        st.subheader("Liste des leads")
        
        # Formatage pour affichage
        display_df = leads_df.copy()
        display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%d/%m/%Y')
        display_df['interest'] = display_df['interest_level'].apply(lambda x: "⭐" * x)
        
        st.dataframe(
            display_df[['name', 'email', 'company', 'status', 'interest', 'created_at', 'user_name']],
            use_container_width=True,
            hide_index=True,
            column_config={
                'name': 'Nom',
                'email': 'Email',
                'company': 'Entreprise',
                'status': 'Statut',
                'interest': 'Intérêt',
                'created_at': 'Créé le',
                'user_name': 'Commercial'
            }
        )
        
        # Export
        export_to_csv(leads_df, "leads")
    else:
        st.info("Aucun lead trouvé")

elif selected == "Prospects":
    # Page Prospects
    st.markdown('<p class="main-header">🎯 Gestion des Prospects</p>', unsafe_allow_html=True)
    
    # Récupération des données
    user_id = None if selected_user == "Tous les utilisateurs" else users_df[users_df['name'] == selected_user]['id'].iloc[0]
    prospects_df = db.get_prospects(user_id)
    
    if prospects_df is not None and not prospects_df.empty:
        # Prospects à relancer aujourd'hui
        today = datetime.now().date()
        prospects_df['next_follow_up'] = pd.to_datetime(prospects_df['next_follow_up'])
        to_follow_up = prospects_df[prospects_df['next_follow_up'].dt.date <= today]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total prospects", len(prospects_df))
        with col2:
            st.metric("À relancer aujourd'hui", len(to_follow_up), 
                     delta=len(to_follow_up), delta_color="inverse")
        
        # Liste des prospects à relancer
        if not to_follow_up.empty:
            st.subheader("⚠️ Prospects à relancer")
            to_follow_up['date_relance'] = to_follow_up['next_follow_up'].dt.strftime('%d/%m/%Y')
            st.dataframe(
                to_follow_up[['name', 'company', 'status', 'date_relance', 'follow_up_strategy', 'user_name']],
                use_container_width=True,
                hide_index=True
            )
        
        # Tous les prospects
        st.subheader("Tous les prospects")
        prospects_df['next_follow_up_formatted'] = prospects_df['next_follow_up'].dt.strftime('%d/%m/%Y')
        prospects_df['interest'] = prospects_df['interest_level'].apply(lambda x: "⭐" * x)
        
        st.dataframe(
            prospects_df[['name', 'company', 'status', 'interest', 'next_follow_up_formatted', 'user_name']],
            use_container_width=True,
            hide_index=True
        )
        
        export_to_csv(prospects_df, "prospects")
    else:
        st.info("Aucun prospect trouvé")

elif selected == "Clients":
    # Page Clients
    st.markdown('<p class="main-header">🤝 Portefeuille Clients</p>', unsafe_allow_html=True)
    
    # Récupération des données
    user_id = None if selected_user == "Tous les utilisateurs" else users_df[users_df['name'] == selected_user]['id'].iloc[0]
    customers_df = db.get_customers(user_id)
    
    if customers_df is not None and not customers_df.empty:
        # Statistiques
        total_revenue = customers_df['revenue'].sum() if 'revenue' in customers_df.columns else 0
        avg_revenue = customers_df['revenue'].mean() if 'revenue' in customers_df.columns else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Nombre de clients", len(customers_df))
        col2.metric("CA Total", format_currency(total_revenue))
        col3.metric("CA Moyen", format_currency(avg_revenue))
        
        # Répartition par secteur
        industry_stats = db.get_customers_by_industry()
        if industry_stats is not None and not industry_stats.empty:
            st.subheader("Répartition par secteur")
            fig = create_bar_chart(industry_stats, 'industry', 'count', "Clients par secteur")
            st.plotly_chart(fig, use_container_width=True)
        
        # Liste des clients
        st.subheader("Liste des clients")
        customers_df['created_at'] = pd.to_datetime(customers_df['created_at']).dt.strftime('%d/%m/%Y')
        customers_df['revenue_formatted'] = customers_df['revenue'].apply(format_currency)
        
        st.dataframe(
            customers_df[['name', 'company', 'industry', 'revenue_formatted', 'created_at', 'user_name']],
            use_container_width=True,
            hide_index=True
        )
        
        export_to_csv(customers_df, "clients")
    else:
        st.info("Aucun client trouvé")

else:  # Rendez-vous
    # Page Rendez-vous
    st.markdown('<p class="main-header">📅 Gestion des Rendez-vous</p>', unsafe_allow_html=True)
    
    # Récupération des données
    user_id = None if selected_user == "Tous les utilisateurs" else users_df[users_df['name'] == selected_user]['id'].iloc[0]
    appointments_df = db.get_appointments(user_id)
    
    if appointments_df is not None and not appointments_df.empty:
        # Conversion des dates
        appointments_df['appointment_date'] = pd.to_datetime(appointments_df['appointment_date'])
        
        # Filtres
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.multiselect(
                "Statut",
                ["Planifié", "Confirmé", "Passé"],
                default=["Planifié", "Confirmé"]
            )
        with col2:
            date_filter = st.date_input(
                "Date",
                value=datetime.now().date()
            )
        
        # Application des filtres
        filtered_df = appointments_df.copy()
        if status_filter:
            filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
        filtered_df = filtered_df[filtered_df['appointment_date'].dt.date == date_filter]
        
        # Timeline
        fig = create_timeline_chart(filtered_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Liste des rendez-vous
        st.subheader(f"Rendez-vous du {date_filter.strftime('%d/%m/%Y')}")
        if not filtered_df.empty:
            filtered_df['heure'] = filtered_df['appointment_date'].dt.strftime('%H:%M')
            filtered_df['date_creation'] = pd.to_datetime(filtered_df['created_at']).dt.strftime('%d/%m/%Y')
            
            st.dataframe(
                filtered_df[['heure', 'title', 'customer_name', 'location', 'status', 'duration', 'user_name']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    'heure': 'Heure',
                    'title': 'Titre',
                    'customer_name': 'Client',
                    'location': 'Lieu',
                    'status': 'Statut',
                    'duration': 'Durée (min)',
                    'user_name': 'Commercial'
                }
            )
        else:
            st.info("Aucun rendez-vous pour cette date")
        
        export_to_csv(appointments_df, "rendez_vous")
    else:
        st.info("Aucun rendez-vous trouvé")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #718096;'>© 2024 AGC-VIE CRM Pro - Tous droits réservés</p>",
    unsafe_allow_html=True
)