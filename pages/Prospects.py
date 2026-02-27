import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from database import db
from utils.helpers import *

st.set_page_config(page_title="Gestion des Prospects", page_icon="🎯", layout="wide")

# CSS personnalisé
st.markdown("""
<style>
    .prospect-card {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 0.75rem;
        border-left: 4px solid;
        transition: all 0.3s;
    }
    .prospect-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .prospect-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2d3748;
    }
    .prospect-company {
        color: #718096;
        font-size: 0.9rem;
    }
    .followup-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .badge-urgent {
        background: #e53e3e20;
        color: #e53e3e;
    }
    .badge-today {
        background: #f6ad5520;
        color: #f6ad55;
    }
    .badge-future {
        background: #38a16920;
        color: #38a169;
    }
    .interest-stars {
        color: #fbbf24;
        font-size: 1.1rem;
    }
    .status-chip {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        display: inline-block;
    }
    .status-nouveau { background: #667eea20; color: #667eea; }
    .status-encours { background: #f6ad5520; color: #f6ad55; }
    .status-relancer { background: #e53e3e20; color: #e53e3e; }
    .status-chaud { background: #f093fb20; color: #f093fb; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="color: #2d3748;">🎯 Gestion des prospects</h1>', unsafe_allow_html=True)

# Récupération des prospects
prospects_df = db.get_prospects()

if prospects_df is not None and not prospects_df.empty:
    # Conversion des dates
    prospects_df['next_follow_up'] = pd.to_datetime(prospects_df['next_follow_up'])
    prospects_df['created_at'] = pd.to_datetime(prospects_df['created_at'])
    prospects_df['date_relance'] = prospects_df['next_follow_up'].dt.date
    prospects_df['jours_restants'] = (prospects_df['next_follow_up'] - datetime.now()).dt.days
    
    # Barre d'outils
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        search_term = st.text_input("🔍 Rechercher", placeholder="Nom, entreprise...")
    
    with col2:
        status_filter = st.multiselect(
            "Statut",
            ["Tous", "Nouveau", "En cours", "À relancer", "Chaud"],
            default=["Nouveau", "En cours", "À relancer"]
        )
    
    with col3:
        followup_filter = st.selectbox(
            "Relance",
            ["Tous", "À relancer aujourd'hui", "En retard", "Cette semaine", "Ce mois"]
        )
    
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Nouveau", use_container_width=True, type="primary"):
            st.session_state.show_add_prospect = True
    
    # Application des filtres
    filtered_df = prospects_df.copy()
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['name'].str.contains(search_term, case=False, na=False) |
            filtered_df['company'].str.contains(search_term, case=False, na=False) |
            filtered_df['email'].str.contains(search_term, case=False, na=False)
        ]
    
    if "Tous" not in status_filter:
        filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
    
    today = datetime.now().date()
    if followup_filter == "À relancer aujourd'hui":
        filtered_df = filtered_df[filtered_df['date_relance'] == today]
    elif followup_filter == "En retard":
        filtered_df = filtered_df[filtered_df['date_relance'] < today]
    elif followup_filter == "Cette semaine":
        end_week = today + timedelta(days=7)
        filtered_df = filtered_df[
            (filtered_df['date_relance'] >= today) &
            (filtered_df['date_relance'] <= end_week)
        ]
    elif followup_filter == "Ce mois":
        end_month = today.replace(day=28) + timedelta(days=4)
        end_month = end_month.replace(day=1) - timedelta(days=1)
        filtered_df = filtered_df[
            (filtered_df['date_relance'] >= today) &
            (filtered_df['date_relance'] <= end_month)
        ]
    
    # KPIs
    st.markdown("### 📊 Vue d'ensemble")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total prospects", len(filtered_df))
    with col2:
        a_relancer = len(filtered_df[filtered_df['date_relance'] <= today])
        st.metric("À relancer", a_relancer, delta=-a_relancer if a_relancer > 0 else 0, delta_color="inverse")
    with col3:
        chauds = len(filtered_df[filtered_df['status'] == 'Chaud'])
        st.metric("Prospects chauds", chauds)
    with col4:
        interet_moyen = filtered_df['interest_level'].mean()
        st.metric("Intérêt moyen", f"{interet_moyen:.1f}/5")
    with col5:
        taux_conversion = (len(filtered_df[filtered_df['status'] == 'Chaud']) / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
        st.metric("Taux conversion potentiel", f"{taux_conversion:.1f}%")
    
    # Graphiques d'analyse
    col1, col2 = st.columns(2)
    
    with col1:
        # Répartition par statut
        status_counts = filtered_df['status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']
        
        fig = px.pie(
            status_counts,
            values='count',
            names='status',
            title="Répartition par statut",
            color_discrete_sequence=['#667eea', '#f6ad55', '#e53e3e', '#f093fb']
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Niveau d'intérêt
        interest_dist = filtered_df['interest_level'].value_counts().sort_index().reset_index()
        interest_dist.columns = ['niveau', 'count']
        
        fig = px.bar(
            interest_dist,
            x='niveau',
            y='count',
            title="Distribution du niveau d'intérêt",
            color='niveau',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(xaxis_title="Niveau d'intérêt", yaxis_title="Nombre")
        st.plotly_chart(fig, use_container_width=True)
    
    # Calendrier des relances
    st.markdown("### 📅 Calendrier des relances")
    
    # Création d'un graphique de timeline pour les relances
    followup_data = filtered_df[filtered_df['next_follow_up'] >= datetime.now()].copy()
    if not followup_data.empty:
        followup_data['date'] = followup_data['next_follow_up'].dt.date
        followup_by_date = followup_data.groupby('date').size().reset_index(name='count')
        
        fig = px.bar(
            followup_by_date,
            x='date',
            y='count',
            title="Relances à venir",
            color='count',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(xaxis_title="Date", yaxis_title="Nombre de relances")
        st.plotly_chart(fig, use_container_width=True)
    
    # Liste des prospects
    st.markdown("### 📋 Liste des prospects")
    
    # Tri des prospects par urgence
    filtered_df['urgence'] = filtered_df['jours_restants'].apply(
        lambda x: 'urgent' if x < 0 else 'today' if x == 0 else 'future'
    )
    
    sorted_df = filtered_df.sort_values(by=['urgence', 'jours_restants'])
    
    # Affichage en cartes
    for _, prospect in sorted_df.iterrows():
        # Déterminer la couleur de la bordure et le badge
        if prospect['jours_restants'] < 0:
            border_color = "#e53e3e"
            badge_class = "badge-urgent"
            badge_text = f"En retard ({abs(prospect['jours_restants'])}j)"
        elif prospect['jours_restants'] == 0:
            border_color = "#f6ad55"
            badge_class = "badge-today"
            badge_text = "Aujourd'hui"
        elif prospect['jours_restants'] <= 7:
            border_color = "#38a169"
            badge_class = "badge-future"
            badge_text = f"J-{prospect['jours_restants']}"
        else:
            border_color = "#718096"
            badge_class = "badge-future"
            badge_text = f"Dans {prospect['jours_restants']}j"
        
        # Badge de statut
        status_class = f"status-{prospect['status'].lower().replace(' ', '').replace('à', '')}"
        
        # Étoiles d'intérêt
        stars = "⭐" * prospect['interest_level']
        
        st.markdown(f"""
        <div class="prospect-card" style="border-left-color: {border_color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span class="prospect-name">{prospect['name']}</span>
                    <span class="prospect-company"> - {prospect['company']}</span>
                </div>
                <div>
                    <span class="status-chip {status_class}">{prospect['status']}</span>
                </div>
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.75rem;">
                <div>
                    📧 {prospect['email']} • 📞 {prospect['phone'] if prospect['phone'] else 'Non renseigné'}
                </div>
                <div class="interest-stars">
                    {stars}
                </div>
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.75rem;">
                <div>
                    <span class="followup-badge {badge_class}">
                        ⏰ Relance: {badge_text}
                    </span>
                </div>
                <div>
                    <button class="btn-contact" onclick="alert('Contacter {prospect['name']}')">📞 Contacter</button>
                </div>
            </div>
            
            {f"<div style='margin-top: 0.75rem; color: #718096; font-style: italic;'>{prospect['notes']}</div>" if prospect['notes'] else ""}
        </div>
        """, unsafe_allow_html=True)
    
    # Export
    st.markdown("---")
    export_to_csv(filtered_df, "prospects")

else:
    st.info("Aucun prospect trouvé dans la base de données")

# Formulaire d'ajout
if st.session_state.get('show_add_prospect', False):
    with st.form("new_prospect_form"):
        st.markdown("### 📝 Nouveau prospect")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nom complet *")
            email = st.text_input("Email *")
            phone = st.text_input("Téléphone")
            company = st.text_input("Entreprise *")
        
        with col2:
            status = st.selectbox("Statut", ["Nouveau", "En cours", "À relancer", "Chaud"])
            interest = st.slider("Niveau d'intérêt", 1, 5, 3)
            followup_date = st.date_input("Date de prochaine relance", datetime.now() + timedelta(days=7))
            strategy = st.text_input("Stratégie de suivi")
        
        notes = st.text_area("Notes")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("✅ Enregistrer")
        with col2:
            if st.form_submit_button("❌ Annuler"):
                st.session_state.show_add_prospect = False
                st.rerun()
        
        if submitted:
            if name and email and company:
                st.success(f"Prospect {name} ajouté avec succès!")
                st.session_state.show_add_prospect = False
                st.rerun()
            else:
                st.error("Veuillez remplir tous les champs obligatoires (*)")