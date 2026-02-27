import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from database import db
from utils.helpers import *

st.set_page_config(page_title="Portefeuille Clients", page_icon="🤝", layout="wide")

# CSS personnalisé
st.markdown("""
<style>
    .client-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 1rem;
    }
    .client-stat {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-left: 4px solid #43e97b;
    }
    .client-name {
        font-size: 1.2rem;
        font-weight: 600;
    }
    .client-detail {
        color: #718096;
        font-size: 0.9rem;
    }
    .revenue-positive {
        color: #38a169;
        font-weight: 600;
    }
    .industry-tag {
        background: #f7fafc;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        color: #4a5568;
        display: inline-block;
        margin-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="color: #2d3748;">🤝 Portefeuille clients</h1>', unsafe_allow_html=True)

# Récupération des clients
customers_df = db.get_customers()

if customers_df is not None and not customers_df.empty:
    # Conversion et préparation des données
    customers_df['created_at'] = pd.to_datetime(customers_df['created_at'])
    customers_df['revenue'] = pd.to_numeric(customers_df['revenue'], errors='coerce')
    
    # Barre d'outils
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        search_term = st.text_input("🔍 Rechercher", placeholder="Nom, entreprise, secteur...")
    
    with col2:
        industry_filter = st.multiselect(
            "Secteur",
            options=customers_df['industry'].dropna().unique().tolist() if 'industry' in customers_df.columns else []
        )
    
    with col3:
        sort_by = st.selectbox(
            "Trier par",
            ["Date (récent)", "CA (décroissant)", "CA (croissant)", "Nom (A-Z)"]
        )
    
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Nouveau", use_container_width=True, type="primary"):
            st.session_state.show_add_client = True
    
    # Application des filtres
    filtered_df = customers_df.copy()
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['name'].str.contains(search_term, case=False, na=False) |
            filtered_df['company'].str.contains(search_term, case=False, na=False) |
            filtered_df['email'].str.contains(search_term, case=False, na=False) |
            filtered_df['industry'].str.contains(search_term, case=False, na=False)
        ]
    
    if industry_filter:
        filtered_df = filtered_df[filtered_df['industry'].isin(industry_filter)]
    
    # Tri
    if sort_by == "Date (récent)":
        filtered_df = filtered_df.sort_values('created_at', ascending=False)
    elif sort_by == "CA (décroissant)":
        filtered_df = filtered_df.sort_values('revenue', ascending=False)
    elif sort_by == "CA (croissant)":
        filtered_df = filtered_df.sort_values('revenue', ascending=True)
    elif sort_by == "Nom (A-Z)":
        filtered_df = filtered_df.sort_values('name')
    
    # KPIs
    st.markdown("### 📊 Performances commerciales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_revenue = filtered_df['revenue'].sum()
    avg_revenue = filtered_df['revenue'].mean()
    top_client = filtered_df.loc[filtered_df['revenue'].idxmax()] if not filtered_df.empty and filtered_df['revenue'].notna().any() else None
    
    with col1:
        st.metric("Nombre de clients", len(filtered_df))
    with col2:
        st.metric("CA Total", format_currency(total_revenue))
    with col3:
        st.metric("CA Moyen", format_currency(avg_revenue))
    with col4:
        if top_client is not None:
            st.metric("Top Client", f"{top_client['name']} - {format_currency(top_client['revenue'])}")
    
    # Graphiques d'analyse
    col1, col2 = st.columns(2)
    
    with col1:
        # Répartition par secteur
        if 'industry' in filtered_df.columns:
            industry_stats = filtered_df['industry'].value_counts().reset_index()
            industry_stats.columns = ['secteur', 'nombre']
            
            fig = px.pie(
                industry_stats.head(10),
                values='nombre',
                names='secteur',
                title="Répartition par secteur d'activité",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Distribution du CA
        fig = px.histogram(
            filtered_df[filtered_df['revenue'].notna()],
            x='revenue',
            nbins=20,
            title="Distribution du chiffre d'affaires",
            color_discrete_sequence=['#43e97b']
        )
        fig.update_layout(
            xaxis_title="Chiffre d'affaires (€)",
            yaxis_title="Nombre de clients"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Top clients
    st.markdown("### 🏆 Top 10 clients")
    
    top_clients = filtered_df.nlargest(10, 'revenue')[['name', 'company', 'industry', 'revenue', 'created_at']].copy()
    top_clients['revenue_formatted'] = top_clients['revenue'].apply(format_currency)
    top_clients['client_depuis'] = pd.to_datetime(top_clients['created_at']).dt.strftime('%d/%m/%Y')
    
    fig = px.bar(
        top_clients,
        x='name',
        y='revenue',
        title="Classement par chiffre d'affaires",
        color='revenue',
        color_continuous_scale='Viridis',
        text='revenue_formatted'
    )
    fig.update_layout(xaxis_title="", yaxis_title="Chiffre d'affaires (€)")
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
    
    # Liste détaillée des clients
    st.markdown("### 📋 Liste complète des clients")
    
    display_df = filtered_df.copy()
    display_df['date_creation'] = display_df['created_at'].dt.strftime('%d/%m/%Y')
    display_df['ca'] = display_df['revenue'].apply(format_currency)
    
    st.dataframe(
        display_df[['name', 'email', 'phone', 'company', 'industry', 'ca', 'date_creation']],
        use_container_width=True,
        hide_index=True,
        column_config={
            'name': 'Nom',
            'email': 'Email',
            'phone': 'Téléphone',
            'company': 'Entreprise',
            'industry': 'Secteur',
            'ca': "Chiffre d'affaires",
            'date_creation': 'Client depuis'
        }
    )
    
    # Vue détaillée d'un client
    st.markdown("### 👤 Détail client")
    
    client_names = ["Sélectionner un client"] + filtered_df['name'].tolist()
    selected_client = st.selectbox("Choisir un client", client_names)
    
    if selected_client != "Sélectionner un client":
        client = filtered_df[filtered_df['name'] == selected_client].iloc[0]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <h3>{client['name']}</h3>
                <p><strong>Entreprise:</strong> {client['company']}</p>
                <p><strong>Email:</strong> {client['email']}</p>
                <p><strong>Téléphone:</strong> {client['phone'] if client['phone'] else 'Non renseigné'}</p>
                <p><strong>Secteur:</strong> {client['industry'] if client['industry'] else 'Non spécifié'}</p>
                <p><strong>Adresse:</strong> {client['address'] if client['address'] else 'Non spécifiée'}</p>
                <p><strong>Chiffre d'affaires:</strong> {format_currency(client['revenue'])}</p>
                <p><strong>Client depuis:</strong> {client['created_at'].strftime('%d/%m/%Y')}</p>
                {f"<p><strong>Notes:</strong> {client['notes']}</p>" if client['notes'] else ""}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### Actions")
            
            if st.button("📧 Envoyer un email", use_container_width=True):
                st.info(f"Ouvrir l'éditeur d'email pour {client['name']}")
            
            if st.button("📅 Planifier un rendez-vous", use_container_width=True):
                st.info(f"Planifier un rendez-vous avec {client['name']}")
            
            if st.button("📊 Voir historique", use_container_width=True):
                st.info(f"Afficher l'historique des interactions avec {client['name']}")
            
            if st.button("✏️ Modifier", use_container_width=True):
                st.info("Fonctionnalité de modification à venir")
    
    # Export
    st.markdown("---")
    export_to_csv(filtered_df, "clients")

else:
    st.info("Aucun client trouvé dans la base de données")

# Formulaire d'ajout
if st.session_state.get('show_add_client', False):
    with st.form("new_client_form"):
        st.markdown("### 📝 Nouveau client")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nom complet *")
            email = st.text_input("Email *")
            phone = st.text_input("Téléphone")
            company = st.text_input("Entreprise *")
        
        with col2:
            industry = st.text_input("Secteur d'activité")
            address = st.text_area("Adresse")
            revenue = st.number_input("Chiffre d'affaires (€)", min_value=0.0, step=1000.0, format="%.2f")
        
        notes = st.text_area("Notes")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("✅ Enregistrer")
        with col2:
            if st.form_submit_button("❌ Annuler"):
                st.session_state.show_add_client = False
                st.rerun()
        
        if submitted:
            if name and email and company:
                st.success(f"Client {name} ajouté avec succès!")
                st.session_state.show_add_client = False
                st.rerun()
            else:
                st.error("Veuillez remplir tous les champs obligatoires (*)")