import numpy as np
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, average_precision_score

# 1. Génération de données hautement déséquilibrées (10 000 transactions, 1% de fraude)
np.random.seed(42)
n_samples = 10000

# Features : Montant, Heure, Distance par rapport au dernier achat, Nombre d'échecs de code
data = {
    'Montant': np.random.exponential(scale=50, size=n_samples), # Majorité de petits montants
    'Distance_Dernier_Achat_KM': np.random.exponential(scale=10, size=n_samples),
    'Echecs_Code_PIN': np.random.choice([0, 1, 2, 3], n_samples, p=[0.95, 0.03, 0.015, 0.005]),
}

df = pd.DataFrame(data)

# Règle de fraude : Montant énorme + distance élevée OU échecs répétés
score_fraude = (df['Montant'] * 0.01) + (df['Distance_Dernier_Achat_KM'] * 0.05) + (df['Echecs_Code_PIN'] * 2)
# On force le top 1% des scores les plus élevés à être de la fraude
seuil = np.percentile(score_fraude, 99)
df['Est_Fraude'] = (score_fraude >= seuil).astype(int)

# 2. Séparation des données
X = df.drop('Est_Fraude', axis=1)
y = df['Est_Fraude']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 3. Normalisation
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 4. Entraînement avec équilibrage des classes (class_weight='balanced')
# C'est l'argument CRUCIAL qui dit au modèle de pénaliser lourdement les erreurs sur la fraude
model = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
model.fit(X_train_scaled, y_train)

# 5. Évaluation orientée "Métiers"
y_pred = model.predict(X_test_scaled)
y_proba = model.predict_proba(X_test_scaled)[:, 1]

print("--- EVALUATION DU MODELE ANTI-FRAUDE ---")
print(classification_report(y_test, y_pred, target_names=['Légitime', 'Fraude']))
print(f"Area Under Precision-Recall Curve (AUPRC) : {average_precision_score(y_test, y_proba):.4f}")

# Sauvegarde des artefacts
with open("fraud_model.pkl", "wb") as f:
    pickle.dump(model, f)
with open("fraud_scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)