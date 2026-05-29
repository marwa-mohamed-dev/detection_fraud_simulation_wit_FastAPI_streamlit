import streamlit as st
import requests
import time
import random
import pandas as pd
import subprocess
import os
import sys

#  Lancement  de FastAPI en tâche de fond sur le Cloud
@st.cache_resource
def start_fastapi_backend():
    """Démarre l'API FastAPI en tâche de fond en s'assurant des chemins d'exécution."""
    # Obtenir le chemin absolu du dossier contenant ce script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
        
    # Lancement d'uvicorn avec l'adresse hôte 0.0.0.0 (universelle sur le cloud)
    process = subprocess.Popen(
        ["uvicorn", "app_fraud:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=current_dir,  # Force le dossier de travail pour qu'uvicorn trouve app_fraud.py
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Attente active pour vérifier si l'API répond
    for _ in range(10):
        time.sleep(1)
        try:
            # On teste la racine de l'API (ou un endpoint existant)
            response = requests.get("http://127.0.0.1:8000/", timeout=1)
            if response.status_code in [200, 404]: # 404 ou 200 signifie que le serveur répond
                break
        except requests.exceptions.ConnectionError:
            continue
            
    return process

# Initialisation automatique du serveur au chargement de la page
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

    st.write("---")
    if st.button("Envoyer la transaction au réseau", use_container_width=True):
        tx_id = f"TX-{random.randint(100000, 999999)}"
        payload = {
            "Transaction_ID": tx_id,
            "Montant": montant,
            "Distance_Dernier_Achat_KM": distance,
            "Echecs_Code_PIN": echecs
        }
        
        try:
            # Appel HTTP à l'API locale
            response = requests.post("http://127.0.0.1:8000/v1/evaluate-transaction", json=payload, timeout=5)
            res = response.json()
            
            # Insertion du résultat en tête de liste pour l'historique
            st.session_state.tx_history.insert(0, {
                "ID": tx_id,
                "Montant": f"{montant:.2f} €",
                "Distance": f"{distance:.1f} KM",
                "Score Risque": f"{res['score_risque']:.1%}",
                "Décision": res['decision']
            })
            st.success(f"Transaction {tx_id} traitée avec succès !")
        except Exception as e:
            st.error(" Erreur : L'API FastAPI sur le port 8000 ne répond pas.")
            # 💡 Affichage de débogage pour comprendre si le processus a planté
            if backend_process.poll() is not None:
                st.warning("Le processus FastAPI s'est arrêté de manière inattendue.")

with col2:
    st.header("Flux des transactions en direct")
    if st.session_state.tx_history:
        df_display = pd.DataFrame(st.session_state.tx_history)
        
        def color_decision(val):
            if val == "BLOCK":
                return 'background-color: #ffcccc; color: #cc0000; font-weight: bold;'
            elif val == "REVIEW_MANUAL":
                return 'background-color: #ffe6cc; color: #cc6600;'
            return 'background-color: #e6ffed; color: #00802b;'
            
        st.dataframe(df_display.style.map(color_decision, subset=['Décision']), use_container_width=True)
    else:
        st.info("En attente de transactions... Utilisez le panneau de gauche pour en générer une.")