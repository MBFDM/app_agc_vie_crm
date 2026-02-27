import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, time
from database import db
from utils.helpers import *

st.set_page_config(page_title="Agenda des rendez-vous", page_icon="📅", layout="wide")

# CSS personnalisé
st.markdown("""
<style>
    .appointment-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 0.75rem;
        border-left: 4px solid;
        transition: transform 0.2s;
    }
    .appointment-card:hover {
        transform: translateX(5px);
    }
    .appointment-time {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2d3748;
    }
    .appointment-title {
        font-size: 1rem;
        font-weight: 500;
        color: #2d3748;
    }
    .appointment-details {
        color: #718096;
        font-size: 0.9rem;
    }
    .calendar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .status-confirmed {
        background: #38a16920;
        color: #38a169;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .status-planned {
        background: #4299e120;
        color: #4299e1;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="color: #2d3748;">📅 Agenda des rendez-vous</h1>', unsafe_allow_html=True)

# Récupération des rendez-vous
appointments_df = db.get_appointments()

if appointments_df is not None and not appointments_df.empty:
    # Conversion des dates
    appointments_df['appointment_date'] = pd.to_datetime(appointments_df['appointment_date'])
    appointments_df['date'] = appointments_df['appointment_date'].dt.date
    appointments_df['heure'] = appointments_df['appointment_date'].dt.strftime('%H:%M')
    
    # Sélecteur de date
    st.markdown('<div class="calendar-header">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        selected_date = st.date_input(
            "📅 Date",
            value=datetime.now().date(),
            min_value=datetime.now().date() - timedelta(days=30),
            max_value=datetime.now().date() + timedelta(days=90)
        )
    
    with col2:
        view_mode = st.radio(
            "Affichage",
            ["Jour", "Semaine", "Mois"],
            horizontal=True
        )
    
    with col3:
        st.markdown(f"<br><div style='text-align: right; font-size: 1.2rem;'>{len(appointments_df)} RDV</div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filtrage selon le mode d'affichage
    if view_mode == "Jour":
        filtered_df = appointments_df[appointments_df['date'] == selected_date]
        st.markdown(f"### 📋 Rendez-vous du {selected_date.strftime('%d/%m/%Y')}")
        
    elif view_mode == "Semaine":
        start_week = selected_date - timedelta(days=selected_date.weekday())
        end_week = start_week + timedelta(days=6)
        filtered_df = appointments_df[
            (appointments_df['date'] >= start_week) &
            (appointments_df['date'] <= end_week)
        ]
        st.markdown(f"### 📋 Rendez-vous du {start_week.strftime('%d/%m')} au {end_week.strftime('%d/%m/%Y')}")
        
    else:  # Mois
        filtered_df = appointments_df[appointments_df['appointment_date'].dt.month == selected_date.month]
        st.markdown(f"### 📋 Rendez-vous de {selected_date.strftime('%B %Y')}")
    
    # Vue calendrier
    if not filtered_df.empty:
        # Création du calendrier visuel
        if view_mode == "Jour":
            # Vue journalière avec timeline
            hours = range(8, 20)  # 8h à 20h
            appointments_by_hour = {hour: [] for hour in hours}
            
            for _, apt in filtered_df.iterrows():
                apt_hour = pd.to_datetime(apt['appointment_date']).hour
                if apt_hour in appointments_by_hour:
                    appointments_by_hour[apt_hour].append(apt)
            
            # Affichage de la timeline
            for hour in hours:
                apts = appointments_by_hour[hour]
                if apts:
                    for apt in apts:
                        border_color = '#38a169' if apt['status'] == 'Confirmé' else '#4299e1'
                        st.markdown(f"""
                        <div class="appointment-card" style="border-left-color: {border_color};">
                            <div style="display: flex; justify-content: space-between;">
                                <div>
                                    <span class="appointment-time">{apt['heure']}</span>
                                    <span class="appointment-title"> - {apt['title']}</span>
                                </div>
                                <span class="{'status-confirmed' if apt['status'] == 'Confirmé' else 'status-planned'}">
                                    {apt['status']}
                                </span>
                            </div>
                            <div class="appointment-details">
                                👤 {apt['customer_name'] if apt['customer_name'] else 'Client non spécifié'} • 
                                📍 {apt['location'] if apt['location'] else 'Lieu non spécifié'} • 
                                ⏱️ {apt['duration']} min
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    if hour == 12:
                        st.markdown("🍽️ **Pause déjeuner**")
                    elif hour < 12 or hour > 14:
                        st.markdown(f"🕐 **{hour:02d}:00** - Disponible")
        
        elif view_mode == "Semaine":
            # Vue hebdomadaire
            days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
            cols = st.columns(7)
            
            for i, col in enumerate(cols):
                current_date = start_week + timedelta(days=i)
                day_appointments = filtered_df[filtered_df['date'] == current_date]
                
                with col:
                    st.markdown(f"**{days[i]}**")
                    st.markdown(f"*{current_date.strftime('%d/%m')}*")
                    st.markdown("---")
                    
                    if not day_appointments.empty:
                        for _, apt in day_appointments.iterrows():
                            color = "🟢" if apt['status'] == 'Confirmé' else "🟡"
                            st.markdown(f"{color} **{apt['heure']}**")
                            st.markdown(f"&nbsp;&nbsp;{apt['title']}")
                            st.markdown(f"&nbsp;&nbsp;👤 {apt['customer_name'] if apt['customer_name'] else 'Client'}")
                            st.markdown("---")
                    else:
                        st.markdown("_Aucun RDV_")
                        st.markdown("---")
        
        else:  # Vue mensuelle
            # Création d'un calendrier mensuel
            import calendar
            cal = calendar.monthcalendar(selected_date.year, selected_date.month)
            
            # En-tête des jours
            days = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
            cols = st.columns(7)
            for i, col in enumerate(cols):
                col.markdown(f"**{days[i]}**")
            
            st.markdown("---")
            
            # Remplir le calendrier
            for week in cal:
                cols = st.columns(7)
                for i, col in enumerate(cols):
                    day = week[i]
                    if day != 0:
                        current_date = datetime(selected_date.year, selected_date.month, day).date()
                        day_appointments = filtered_df[filtered_df['date'] == current_date]
                        
                        with col:
                            st.markdown(f"**{day}**")
                            if not day_appointments.empty:
                                count = len(day_appointments)
                                confirmed = len(day_appointments[day_appointments['status'] == 'Confirmé'])
                                st.markdown(f"📅 {count} RDV")
                                if confirmed > 0:
                                    st.markdown(f"✅ {confirmed} confirmés")
                            else:
                                st.markdown("_ _")
        
        # Liste détaillée
        st.markdown("### 📋 Liste détaillée")
        
        display_df = filtered_df.copy()
        display_df['date_heure'] = pd.to_datetime(display_df['appointment_date']).dt.strftime('%d/%m/%Y %H:%M')
        display_df['client'] = display_df['customer_name'].fillna('Non spécifié')
        display_df['lieu'] = display_df['location'].fillna('Non spécifié')
        
        st.dataframe(
            display_df[['date_heure', 'title', 'client', 'lieu', 'duration', 'status']],
            use_container_width=True,
            hide_index=True,
            column_config={
                'date_heure': 'Date et heure',
                'title': 'Titre',
                'client': 'Client',
                'lieu': 'Lieu',
                'duration': 'Durée (min)',
                'status': 'Statut'
            }
        )
        
        # Statistiques
        st.markdown("### 📊 Statistiques")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total RDV", len(filtered_df))
        with col2:
            st.metric("Confirmés", len(filtered_df[filtered_df['status'] == 'Confirmé']))
        with col3:
            st.metric("Durée moyenne", f"{filtered_df['duration'].mean():.0f} min")
        with col4:
            st.metric("Planifiés", len(filtered_df[filtered_df['status'] == 'Planifié']))
        
    else:
        st.info(f"Aucun rendez-vous trouvé pour la période sélectionnée")
    
    # Formulaire d'ajout rapide
    with st.expander("➕ Ajouter un rendez-vous"):
        with st.form("new_appointment_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Titre du rendez-vous *")
                customer = st.text_input("Nom du client")
                date = st.date_input("Date *", datetime.now())
                time_input = st.time_input("Heure *", time(9, 0))
            
            with col2:
                location = st.text_input("Lieu")
                duration = st.number_input("Durée (minutes)", 15, 240, 60, step=15)
                status = st.selectbox("Statut", ["Planifié", "Confirmé"])
                notes = st.text_area("Notes")
            
            submitted = st.form_submit_button("✅ Créer le rendez-vous")
            
            if submitted:
                if title:
                    st.success(f"Rendez-vous '{title}' créé avec succès!")
                    st.rerun()
                else:
                    st.error("Le titre est obligatoire")

else:
    st.info("Aucun rendez-vous trouvé dans la base de données")

# Export
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("📥 Exporter en CSV", use_container_width=True):
        if appointments_df is not None and not appointments_df.empty:
            csv = appointments_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger",
                data=csv,
                file_name=f"rendez_vous_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )

with col2:
    if st.button("📅 Synchroniser Google Calendar", use_container_width=True):
        st.info("Fonctionnalité à venir")