import pickle
import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# CONFIGURATION CHEMINS ABSOLUS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "fraud_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "fraud_scaler.pkl")

# Chargement sécurisé du modèle anti-fraude
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)
with open(SCALER_PATH, "rb") as f:
    scaler = pickle.load(f)

app = FastAPI(title="Moteur de Risque Transactionnel Temps Réel", version="1.0")

class Transaction(BaseModel):
    Transaction_ID: str
    Montant: float
    Distance_Dernier_Achat_KM: float
    Echecs_Code_PIN: int

@app.post("/v1/evaluate-transaction")
def evaluate_transaction(tx: Transaction):
    # Formater les données pour le modèle
    input_data = pd.DataFrame([{
        'Montant': tx.Montant,
        'Distance_Dernier_Achat_KM': tx.Distance_Dernier_Achat_KM,
        'Echecs_Code_PIN': tx.Echecs_Code_PIN
    }])
    
    # Inférence
    input_scaled = scaler.transform(input_data)
    score_risque = float(model.predict_proba(input_scaled)[0][1])
    
    # Logique métier de blocage (Seuil à 65% de certitude)
    decision = "APPROVE"
    if score_risque >= 0.65:
        decision = "BLOCK"
    elif score_risque >= 0.40:
        decision = "REVIEW_MANUAL"
        
    return {
        "transaction_id": tx.Transaction_ID,
        "score_risque": round(score_risque, 4),
        "decision": decision,
        "action_requise": "Aucune" if decision == "APPROVE" else "Déclencher protocole de sécurité"
    }