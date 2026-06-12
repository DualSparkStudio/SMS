# Data Flow Diagrams

## DFD Level 0 (Context Diagram)

```mermaid
flowchart LR
    USER[User] -->|SMS Text| TG[TextGuard Platform]
    TG -->|Analysis Results| USER
    TG -->|Analytics| ADMIN[Admin]
    ADMIN -->|Train/Configure| TG
    TG -->|Store Data| DB[(Database)]
    DB -->|Retrieve| TG
```

## DFD Level 1

```mermaid
flowchart TB
    USER[User] -->|SMS| P1[1.0 SMS Analysis]
    P1 -->|Results| USER
    P1 -->|Store| D1[(SMS Messages DB)]
    P1 --> P2[2.0 HASDF Pipeline]
    P2 --> P3[3.0 ML Prediction]
    P2 --> P4[4.0 XAI Explanation]
    P2 --> P5[5.0 Phishing Analysis]
    P2 --> P6[6.0 Fraud Detection]
    USER -->|Feedback| P7[7.0 Continuous Learning]
    P7 -->|Retrain| P3
    P7 --> D2[(Feedback DB)]
    D1 --> P8[8.0 Campaign Detection]
    P8 --> D3[(Campaigns DB)]
    D1 --> P9[9.0 Analytics Dashboard]
    P9 -->|Charts| ADMIN[Admin/User]
    USER -->|Chat Query| P10[10.0 AI Assistant]
    P10 -->|Response| USER
    D1 --> P10
```

## DFD Level 2 — HASDF Pipeline Detail

```mermaid
flowchart TB
    INPUT[SMS Input] --> LD[2.1 Language Detection]
    LD -->|Non-English| TR[2.2 Translation]
    LD -->|English| URL[2.3 URL Extraction]
    TR --> URL
    URL --> PA[2.4 Phishing Analysis]
    PA --> FD[2.5 Fraud Pattern Match]
    FD --> ML[2.6 ML Classifier]
    ML --> XAI[2.7 XAI Layer]
    XAI --> SS[2.8 Security Score]
    SS --> OUT[Analysis Output]
    OUT --> CD[2.9 Campaign Clustering]
    OUT --> FB[2.10 Feedback Store]
    FB --> RT[2.11 Model Retraining]
    RT --> ML
```

## Data Stores

| Store | Contents |
|-------|----------|
| D1 — SMS Messages | Message text, predictions, XAI data, timestamps |
| D2 — Feedback | User corrections for continuous learning |
| D3 — Campaigns | Clustered spam campaign data |
| D4 — Model Metrics | Training history and comparison results |
