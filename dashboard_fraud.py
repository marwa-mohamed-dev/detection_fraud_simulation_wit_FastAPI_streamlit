import streamlit as st
import requests
import time
import random
import pandas as pd
import subprocess  # 👈 AJOUT: Pour lancer des processus en arrière-plan

# Lancement automatique de FastAPI en tâche de fond sur le Cloud
@st.cache_resource
def start_fastapi_backend():
    """Démarre l'API FastAPI à l'aide d'un sous-processus uvicorn."""
    process = subprocess.Popen(
        ["uvicorn", "app_fraud:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(2)  # Laisse 2 secondes à l'API pour s'initialiser proprement
    return process

# Initialisation du serveur au chargement de la page
backend_process = start_fastapi_backend()

st.set_page_config(page_title="Fraud Watch - Security Dashboard", page_icon="🛡️", layout="wide")

st.title("🛡️ Fraud Watch : Moteur de Décision en Temps Réel")
st.write("Simulation de flux de transactions bancaires en direct.")

# Initialiser un historique des transactions évaluées dans la session
if 'tx_history' not in st.session_state:
    st.session_state.tx_history = []

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Simuler une transaction")
    
    #  Raccourcis de simulation automatique
    st.subheader("Raccourcis scénarios")
    scenario = st.radio(
        "Choisir un profil type :",
        ["Manuel", "Achat Standard (Sain)", "Voyage Suspect (Review)", "Brute-Force & Gros Montant (Fraude)"]
    )
    
    # Configuration des valeurs par défaut selon le scénario sélectionné
    if scenario == "Achat Standard (Sain)":
        default_montant = 35.0
        default_distance = 1.2
        default_echecs = 0
    elif scenario == "Voyage Suspect (Review)":
        default_montant = 180.0
        default_distance = 120.0
        default_echecs = 1
    elif scenario == "Brute-Force & Gros Montant (Fraude)":
        default_montant = 1500.0
        default_distance = 850.0
        default_echecs = 3
    else:
        default_montant = 45.0
        default_distance = 2.5
        default_echecs = 0

    # Inputs Streamlit connectés aux valeurs par défaut
    montant = st.number_input("Montant de la transaction (€)", min_value=0.5, max_value=5000.0, value=default_montant)
    distance = st.number_input("Distance depuis le dernier achat (KM)", min_value=0.0, max_value=20000.0, value=default_distance)
    echecs = st.slider("Nombre d'échecs code PIN consécutifs", min_value=0, max_value=3, value=default_echecs)

with col2:
    st.header("Flux des transactions en direct")
    if st.session_state.tx_history:
        # Transformation en DataFrame pour un affichage propre
        df_display = pd.DataFrame(st.session_state.tx_history)
        
        # Fonction de coloration pour l'interface
        def color_decision(val):
            if val == "BLOCK":
                return 'background-color: #ffcccc; color: #cc0000; font-weight: bold;'
            elif val == "REVIEW_MANUAL":
                return 'background-color: #ffe6cc; color: #cc6600;'
            return 'background-color: #e6ffed; color: #00802b;'
            
        st.dataframe(df_display.style.applymap(color_decision, subset=['Décision']), use_container_width=True)
    else:
        st.info("En attente de transactions... Utilisez le panneau de gauche pour en générer une.")