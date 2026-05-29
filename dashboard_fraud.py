import streamlit as st
import time
import random
import pandas as pd
import os
import sys
import pickle

st.set_page_config(page_title="Fraud Watch - Security Dashboard", layout="wide")

# 1. Chargement direct des modèles en mémoire
@st.cache_resource
def load_fraud_models():
    """Verifie l'existence des fichiers pkl, les genere si besoin, et les charge en memoire."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    model_path = os.path.join(current_dir, "fraud_model.pkl")
    scaler_path = os.path.join(current_dir, "fraud_scaler.pkl")
    
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        with st.spinner("Premier demarrage : Entrainement du modele anti-fraude en cours..."):
            import subprocess
            subprocess.run([sys.executable, "train_fraud.py"], cwd=current_dir)
            time.sleep(2)
            
    with open(model_path, "rb") as f:
        loaded_model = pickle.load(f)
    with open(scaler_path, "rb") as f:
        loaded_scaler = pickle.load(f)
        
    return loaded_model, loaded_scaler

try:
    model, scaler = load_fraud_models()
except Exception as e:
    st.error(f"Erreur lors du chargement des modèles : {e}")

st.title("Fraud Watch : Moteur de Décision en Temps Réel")
st.write("Simulation de flux de transactions bancaires en direct sur le Cloud.")

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
    
    if scenario == "Achat Standard (Sain)":
        default_montant, default_distance, default_echecs = 35.0, 1.2, 0
    elif scenario == "Voyage Suspect (Review)":
        default_montant, default_distance, default_echecs = 180.0, 120.0, 1
    elif scenario == "Brute-Force & Gros Montant (Fraude)":
        default_montant, default_distance, default_echecs = 1500.0, 850.0, 3
    else:
        default_montant, default_distance, default_echecs = 45.0, 2.5, 0

    montant = st.number_input("Montant de la transaction (EUR)", min_value=0.5, max_value=5000.0, value=default_montant)
    distance = st.number_input("Distance depuis le dernier achat (KM)", min_value=0.0, max_value=20000.0, value=default_distance)
    echecs = st.slider("Nombre d'échecs code PIN consécutifs", min_value=0, max_value=3, value=default_echecs)

    st.write("---")
    if st.button("Envoyer la transaction au réseau", use_container_width=True):
        tx_id = f"TX-{random.randint(100000, 999999)}"
        
        # Inférence directe
        input_data = pd.DataFrame([{
            'Montant': montant,
            'Distance_Dernier_Achat_KM': distance,
            'Echecs_Code_PIN': echecs
        }])
        
        input_scaled = scaler.transform(input_data)
        score_risque = float(model.predict_proba(input_scaled)[0][1])
        
        if score_risque >= 0.65:
            decision = "BLOCK"
        elif score_risque >= 0.35:
            decision = "REVIEW_MANUAL"
        else:
            decision = "APPROVE"
            
        st.session_state.tx_history.insert(0, {
            "ID": tx_id,
            "Montant": f"{montant:.2f} EUR",
            "Distance": f"{distance:.1f} KM",
            "Score Risque": f"{score_risque:.1%}",
            "Décision": decision
        })
        st.success(f"Transaction {tx_id} évaluée localement avec succès.")

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
        st.info("En attente de transactions... Utilisez le panneau de gauche pour envoyer un flux.")