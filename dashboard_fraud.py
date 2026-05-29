import streamlit as st
import requests
import time
import random
import pandas as pd

st.set_page_config(page_title="Fraud Watch - Security Dashboard", page_icon="🛡️", layout="wide")

st.title("🛡️ Fraud Watch : Moteur de Décision en Temps Réel")
st.write("Simulation de flux de transactions bancaires en direct.")

# Initialiser un historique des transactions évaluées dans la session
if 'tx_history' not in st.session_state:
    st.session_state.tx_history = []

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Simuler une transaction")
    montant = st.number_input("Montant de la transaction (€)", min_value=0.5, max_value=5000.0, value=45.0)
    distance = st.number_input("Distance depuis le dernier achat (KM)", min_value=0.0, max_value=20000.0, value=2.5)
    echecs = st.slider("Nombre d'échecs code PIN consécutifs", min_value=0, max_value=3, value=0)
    
    if st.button("Envoyer la transaction au réseau"):
        tx_id = f"TX-{random.randint(100000, 999999)}"
        payload = {
            "Transaction_ID": tx_id,
            "Montant": montant,
            "Distance_Dernier_Achat_KM": distance,
            "Echecs_Code_PIN": echecs
        }
        
        try:
            res = requests.post("http://127.0.0.1:8000/v1/evaluate-transaction", json=payload).json()
            # Ajouter au début de notre liste historique
            st.session_state.tx_history.insert(0, {
                "ID": tx_id,
                "Montant": f"{montant} €",
                "Distance": f"{distance} KM",
                "Score Risque": f"{res['score_risque']:.1%}",
                "Décision": res['decision']
            })
        except:
            st.error("L'API FastAPI sur le port 8000 n'est pas lancée.")

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