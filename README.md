# Fraud Watch: Real-Time Transaction Risk Scoring Engine

A production-ready, decoupled Machine Learning architecture designed to ingest financial transaction properties, evaluate risk signals, and serve immediate fraud mitigation actions. The system is engineered to handle highly imbalanced datasets using a cost-sensitive Random Forest architecture, serving decisions via a RESTful API and visualizing metrics through an interactive security console.

---

## 🚀 Architecture Components

* **Cost-Sensitive Training Engine (`train_fraud.py`):** Trains a `RandomForestClassifier` on heavily imbalanced transaction logs (1% fraud baseline). It utilizes balanced class weighting to heavily penalize false negatives (missed fraud) and monitors Precision-Recall trade-offs.
* **Low-Latency Inference Backend (`app_fraud.py`):** A high-performance **FastAPI** wrapper that exposes an endpoint for real-time risk assessment. It validates payloads natively via Pydantic and applies conditional automated blocking thresholds.
* **Security Operations Center Dashboard (`dashboard_fraud.py`):** An interactive **Streamlit** user interface acting as a live network simulator, allowing analysts to manually submit transactions and observe real-time decision stream logs.

---

## 📊 Analytical Framework & Features

The inference engine evaluates risks based on three core transactional features:

| Feature Variable | Operational Context | Risk Metric Vector |
| :--- | :--- | :--- |
| `Montant` | Transaction volume in Euros (€) | Exponential distribution (heavy-tailed) |
| `Distance_Dernier_Achat_KM` | Kilometric distance from the user's last known location | Anomalous geographical displacement |
| `Echecs_Code_PIN` | Cumulative consecutive failed PIN entries (0 to 3) | Immediate credential brute-force indicator |

### Automated Decision Logic
* **`APPROVE`** (Risk Score $< 35\%$): Transaction cleared automatically.
* **`REVIEW_MANUAL`** ($35\% \le$ Risk Score $< 65\%$): Transaction allowed but flagged for asynchronous audit.
* **`BLOCK`** (Risk Score $\ge 65\%$): Automated structural rejection to mitigate immediate financial leakage.

---
