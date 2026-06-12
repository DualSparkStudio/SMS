# TextGuard — AI-Powered Intelligent SMS Security and Spam Detection Platform

**M.E. Dissertation Project** | Hybrid Adaptive Spam Detection Framework (HASDF)

## Overview

Research-grade full-stack platform for SMS spam detection using Machine Learning, Explainable AI (SHAP/LIME), phishing URL analysis, fraud pattern detection, multilingual support (English/Hindi/Marathi), campaign clustering, and continuous learning.

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React, Bootstrap 5, Chart.js, Axios, React Router |
| Backend | Python, Django, Django REST Framework |
| ML/AI | Scikit-Learn, TensorFlow, Transformers, NLTK, SpaCy, SHAP, LIME |
| Database | MySQL (SQLite for local dev) |
| Deployment | Docker, Nginx |

## Quick Start (Local Development)

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py train_models
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Django Admin: http://localhost:8000/admin/

## Docker Deployment

```bash
docker-compose up --build
```

- App: http://localhost
- API: http://localhost/api/

## HASDF Pipeline

1. SMS Received → 2. Language Detection → 3. URL Analysis → 4. Fraud Pattern Analysis → 5. ML Prediction → 6. Explainable AI → 7. Security Score → 8. Campaign Detection → 9. Feedback Learning

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sms/analyze/` | Analyze SMS message |
| GET | `/api/sms/{id}/` | Get analysis results |
| POST | `/api/sms/feedback/` | Submit prediction feedback |
| GET | `/api/analytics/dashboard/` | Dashboard charts data |
| GET | `/api/campaigns/` | List spam campaigns |
| POST | `/api/chat/` | AI assistant chat |
| GET | `/api/ml/comparison/` | Model comparison metrics |
| POST | `/api/auth/register/` | User registration |
| POST | `/api/auth/login/` | JWT login |

See [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for full API reference.

## Project Structure

```
TextGuard/
├── backend/           # Django REST API
│   ├── accounts/      # Authentication
│   ├── sms_analysis/  # SMS analysis & feedback
│   ├── ml_engine/     # HASDF pipeline & ML models
│   ├── analytics/     # Dashboard analytics
│   ├── campaigns/     # Campaign clustering
│   └── chatbot/       # AI assistant
├── frontend/          # React SPA
├── ml_models/         # Trained model artifacts
├── docker/            # Docker & Nginx config
└── docs/              # Dissertation documentation
```

## Documentation

- [Architecture Diagram](docs/ARCHITECTURE.md)
- [ER Diagram](docs/ER_DIAGRAM.md)
- [DFD Level 0, 1, 2](docs/DFD.md)
- [UML Diagrams](docs/UML.md)
- [API Documentation](docs/API_DOCUMENTATION.md)
- [Testing Documentation](docs/TESTING.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## License

Academic / Dissertation Project
