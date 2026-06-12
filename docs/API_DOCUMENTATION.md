# API Documentation — TextGuard Platform

Base URL: `http://localhost:8000/api`

Authentication: JWT Bearer token (except public endpoints)

---

## Authentication

### Register
```
POST /auth/register/
```
```json
{
  "username": "john",
  "email": "john@example.com",
  "first_name": "John",
  "password": "securepass123",
  "password_confirm": "securepass123"
}
```

### Login
```
POST /auth/login/
```
```json
{
  "email": "john@example.com",
  "password": "securepass123"
}
```
Response:
```json
{
  "access": "eyJ...",
  "refresh": "eyJ..."
}
```

### Profile
```
GET /auth/profile/
Authorization: Bearer <token>
```

---

## SMS Analysis

### Analyze SMS
```
POST /sms/analyze/
```
```json
{
  "message": "Congratulations! You won Rs 50000. Click here to claim."
}
```

Response (201):
```json
{
  "id": 1,
  "message": "...",
  "prediction": "spam",
  "confidence": 0.98,
  "language": "en",
  "security_score": 15,
  "fraud_type": "Lottery Scam",
  "explanation": {
    "classification": "SPAM",
    "confidence_percent": 98.0,
    "reasons": ["Fraud type: Lottery Scam", "Suspicious link detected"]
  },
  "phishing_analysis": { "urls_found": [], "max_risk": 0 },
  "xai_data": {
    "word_impact_table": [
      { "word": "Won", "impact": "High", "contribution": 0.25 }
    ]
  },
  "hasadf_pipeline": [
    { "step": 1, "name": "SMS Received", "status": "completed" }
  ]
}
```

### Get SMS Detail
```
GET /sms/{id}/
```

### SMS History (Authenticated)
```
GET /sms/history/
Authorization: Bearer <token>
```

### Submit Feedback
```
POST /sms/feedback/
Authorization: Bearer <token>
```
```json
{
  "sms_id": 1,
  "feedback": "correct"
}
```

---

## Analytics

### Dashboard
```
GET /analytics/dashboard/
```

### Learning Dashboard
```
GET /analytics/learning/
```

---

## Campaigns

### List Campaigns
```
GET /campaigns/
```

### Detect Campaigns (Admin)
```
POST /campaigns/detect/
Authorization: Bearer <admin_token>
```

---

## AI Chatbot

### Chat
```
POST /chat/
```
```json
{
  "message": "Why is this SMS dangerous?",
  "sms_id": 1
}
```

---

## ML Engine

### Model Comparison
```
GET /ml/comparison/
```

### Train Models (Admin)
```
POST /ml/train/
```
```json
{
  "include_feedback": true
}
```

---

## Error Responses

| Code | Description |
|------|-------------|
| 400 | Bad Request — invalid input |
| 401 | Unauthorized — missing/invalid token |
| 403 | Forbidden — insufficient permissions |
| 404 | Not Found |
| 500 | Internal Server Error |
