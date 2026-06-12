# System Architecture — TextGuard Platform

## High-Level Architecture

```mermaid
graph TB
    subgraph Client["Client Layer"]
        WEB[React Web App]
        MOB[Mobile Browser]
    end

    subgraph Gateway["API Gateway"]
        NGINX[Nginx Reverse Proxy]
    end

    subgraph Backend["Django Backend"]
        API[Django REST Framework]
        AUTH[JWT Authentication]
        HASDF[HASDF Pipeline]
        ML[ML Engine]
        XAI[Explainable AI]
        PHISH[Phishing Detector]
        FRAUD[Fraud Detector]
        CAMP[Campaign Clustering]
        CHAT[AI Chatbot]
    end

    subgraph Data["Data Layer"]
        MYSQL[(MySQL Database)]
        MODELS[(ML Model Store)]
    end

    WEB --> NGINX
    MOB --> NGINX
    NGINX --> API
    API --> AUTH
    API --> HASDF
    HASDF --> ML
    HASDF --> XAI
    HASDF --> PHISH
    HASDF --> FRAUD
    HASDF --> CAMP
    API --> CHAT
    API --> MYSQL
    ML --> MODELS
```

## HASDF Framework Architecture

```mermaid
flowchart LR
    A[SMS Input] --> B[Language Detection]
    B --> C[URL Analysis]
    C --> D[Fraud Pattern Analysis]
    D --> E[ML Prediction]
    E --> F[Explainable AI]
    F --> G[Security Score]
    G --> H[Campaign Detection]
    H --> I[User Feedback Learning]
    I --> E
```

## Component Description

| Component | Technology | Responsibility |
|-----------|-----------|----------------|
| React Frontend | React 18, Bootstrap 5 | User interface, charts, forms |
| Django REST API | Django 4.2, DRF | Business logic, API endpoints |
| HASDF Pipeline | Python | Orchestrates all analysis modules |
| ML Engine | Scikit-Learn | Spam/ham classification |
| XAI Module | SHAP/LIME hybrid | Word-level explanations |
| Phishing Module | tldextract, regex | URL risk analysis |
| Fraud Module | Pattern matching | Banking/lottery/job/investment fraud |
| Campaign Module | Clustering | Spam campaign detection |
| Chatbot | Rule-based NLP | Security guidance |

## Deployment Architecture

```mermaid
graph LR
    USER[Users] --> LB[Nginx]
    LB --> FE[React Static Files]
    LB --> BE[Django + Gunicorn]
    BE --> DB[(MySQL)]
    BE --> FS[Model Files]
```
