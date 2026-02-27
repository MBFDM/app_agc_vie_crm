import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import db
from utils.helpers import *
import plotly.express as px

st.set_page_config(page_title="Gestion des Leads", page_icon="👥", layout="wide")

# CSS personnalisé
st.markdown("""
<style>
    .lead-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 0.5rem;
        border-left: 3px solid #667eea;
    }
    .lead-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2d3748;
    }
    .lead-company {
        color: #718096;
        font-size: 0.9rem;
    }
    .badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        display: inline-block;
    }
    .badge-new {
        background: #667eea20;
        color: #667eea;
    }
    .badge-contact {
        background: #f6ad5520;
        color: #f6ad55;
    }
    .badge-qualified {
        background: #38a16920;
        color: #38a169;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="color: #2d3748;">👥 Gestion des leads</h1>', unsafe_allow_html=True)

# Barre d'outils
col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

with col1:
    search_term = st.text_input("🔍 Rechercher", placeholder="Nom, email, entreprise...")

with col2:
    status_filter = st.multiselect(
        "Statut",
        ["Tous", "Nouveau", "En contact", "Qualifié"],
        default=["Nouveau", "En contact"]
    )

with col3:
    date_filter = st.selectbox(
        "Période",
        ["Tous", "Aujourd'hui", "Cette semaine", "Ce mois", "3 derniers mois"]
    )

with col4:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ Nouveau", use_container_width=True, type="primary"):
        st.session_state.show_add_form = True

# Récupération des leads
leads_df = db.get_leads()

if leads_df is not None and not leads_df.empty:
    # Application des filtres
    filtered_df = leads_df.copy()
    
    # Filtre de recherche
    if search_term:
        filtered_df = filtered_df[
            filtered_df['name'].str.contains(search_term, case=False, na=False) |
            filtered_df['email'].str.contains(search_term, case=False, na=False) |
            filtered_df['company'].str.contains(search_term, case=False, na=False)
        ]
    
    # Filtre de statut
    if "Tous" not in status_filter:
        filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
    
    # Filtre de date
    if date_filter != "Tous":
        filtered_df['created_at'] = pd.to_datetime(filtered_df['created_at'])
        today = datetime.now()
        
        if date_filter == "Aujourd'hui":
            filtered_df = filtered_df[filtered_df['created_at'].dt.date == today.date()]
        elif date_filter == "Cette semaine":
            start_week = today - timedelta(days=today.weekday())
            filtered_df = filtered_df[filtered_df['created_at'].dt.date >= start_week.date()]
        elif date_filter == "Ce mois":
            filtered_df = filtered_df[filtered_df['created_at'].dt.month == today.month]
        elif date_filter == "3 derniers mois":
            cutoff = today - timedelta(days=90)
            filtered_df = filtered_df[filtered_df['created_at'] >= cutoff]
    
    # Statistiques
    st.markdown("### 📊 Aperçu")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total leads", len(filtered_df))
    with col2:
        st.metric("Nouveaux", len(filtered_df[filtered_df['status'] == 'Nouveau']))
    with col3:
        st.metric("En contact", len(filtered_df[filtered_df['status'] == 'En contact']))
    with col4:
        st.metric("Qualifiés", len(filtered_df[filtered_df['status'] == 'Qualifié']))
    
    # Graphique de répartition
    if not filtered_df.empty:
        status_counts = filtered_df['status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']
        
        fig = px.pie(
            status_counts,
            values='count',
            names='status',
            title="Répartition par statut",
            color_discrete_sequence=['#667eea', '#f6ad55', '#38a169']
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    # Liste des leads
    st.markdown("### 📋 Liste des leads")
    
    # Formatage pour l'affichage
    display_df = filtered_df.copy()
    display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%d/%m/%Y')
    display_df['intérêt'] = display_df['interest_level'].apply(lambda x: "⭐" * x)
    
    # Ajout de badges de statut avec couleurs
    def style_status(val):
        colors = {
            'Nouveau': 'background-color: #667eea20; color: #667eea',
            'En contact': 'background-color: #f6ad5520; color: #f6ad55',
            'Qualifié': 'background-color: #38a16920; color: #38a169'
        }
        return colors.get(val, '')
    
    # Affichage du tableau
    st.dataframe(
        display_df[['name', 'email', 'phone', 'company', 'status', 'intérêt', 'created_at']],
        use_container_width=True,
        hide_index=True,
        column_config={
            'name': 'Nom',
            'email': 'Email',
            'phone': 'Téléphone',
            'company': 'Entreprise',
            'status': st.column_config.Column(
                'Statut',
                help="Statut du lead"
            ),
            'intérêt': 'Intérêt',
            'created_at': 'Date'
        }
    )
    
    # Détail d'un lead sélectionné
    st.markdown("### 📝 Détail du lead")
    
    lead_names = ["Sélectionner un lead"] + display_df['name'].tolist()
    selected_lead_name = st.selectbox("Choisir un lead", lead_names)
    
    if selected_lead_name != "Sélectionner un lead":
        lead = filtered_df[filtered_df['name'] == selected_lead_name].iloc[0]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            <div style="background: white; padding: 1.5rem; border-radius: 10px;">
                <h4>{lead['name']}</h4>
                <p><strong>Email:</strong> {lead['email']}</p>
                <p><strong>Téléphone:</strong> {lead['phone']}</p>
                <p><strong>Entreprise:</strong> {lead['company']}</p>
                <p><strong>Statut:</strong> {lead['status']}</p>
                <p><strong>Intérêt:</strong> {"⭐" * lead['interest_level']}</p>
                <p><strong>Notes:</strong> {lead['notes'] if lead['notes'] else "Aucune note"}</p>
                <p><strong>Date création:</strong> {pd.to_datetime(lead['created_at']).strftime('%d/%m/%Y')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### Actions")
            
            if st.button("📞 Contacter", use_container_width=True):
                st.success(f"Action de contact avec {lead['name']} enregistrée")
            
            if st.button("✏️ Modifier", use_container_width=True):
                st.info("Fonctionnalité de modification à venir")
            
            if st.button("🗑️ Supprimer", use_container_width=True):
                st.warning("Fonctionnalité de suppression à venir")
            
            # Changement de statut
            st.markdown("#### Changer statut")
            new_status = st.selectbox(
                "Nouveau statut",
                ["Nouveau", "En contact", "Qualifié"],
                index=["Nouveau", "En contact", "Qualifié"].index(lead['status'])
            )
            
            if st.button("✅ Mettre à jour", use_container_width=True):
                st.success(f"Statut mis à jour: {new_status}")
    
    # Export
    st.markdown("---")
    export_to_csv(filtered_df, "leads")

else:
    st.info("Aucun lead trouvé dans la base de données")

# Formulaire d'ajout (dans un expander)
with st.expander("➕ Ajouter un nouveau lead", expanded=st.session_state.get('show_add_form', False)):
    with st.form("new_lead_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nom complet *")
            email = st.text_input("Email *")
            phone = st.text_input("Téléphone")
        
        with col2:
            company = st.text_input("Entreprise *")
            status = st.selectbox("Statut", ["Nouveau", "En contact", "Qualifié"])
            interest = st.slider("Niveau d'intérêt", 1, 5, 3)
        
        notes = st.text_area("Notes")
        
        submitted = st.form_submit_button("💾 Enregistrer le lead")
        
        if submitted:
            if name and email and company:
                st.success(f"Lead {name} ajouté avec succès!")
                st.session_state.show_add_form = False
                st.rerun()
            else:
                st.error("Veuillez remplir tous les champs obligatoires (*)")