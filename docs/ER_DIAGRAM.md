# Entity-Relationship Diagram

## ER Diagram

```mermaid
erDiagram
    USERS {
        int id PK
        string username
        string email UK
        string password
        string first_name
        string last_name
        boolean is_admin_user
        datetime date_joined
    }

    SMS_MESSAGES {
        int id PK
        int user_id FK
        text message
        string prediction
        float confidence
        string language
        int security_score
        string fraud_type
        json explanation
        json phishing_analysis
        json xai_data
        json suspicious_words
        json urls_found
        json hasadf_pipeline
        datetime timestamp
    }

    FEEDBACK {
        int id PK
        int user_id FK
        int sms_id FK
        string feedback
        string corrected_label
        datetime timestamp
    }

    CAMPAIGNS {
        int id PK
        string campaign_name
        json cluster_keywords
        json sample_messages
        int affected_users
        int message_count
        float risk_score
        string risk_level
        string campaign_type
        datetime detected_at
        boolean is_active
    }

    MODEL_TRAINING_LOGS {
        int id PK
        datetime trained_at
        int samples_count
        float accuracy
        float precision
        float recall
        float f1_score
        string model_name
        boolean included_feedback
    }

    USERS ||--o{ SMS_MESSAGES : submits
    USERS ||--o{ FEEDBACK : provides
    SMS_MESSAGES ||--o{ FEEDBACK : receives
```

## Relationships

| Relationship | Type | Description |
|-------------|------|-------------|
| User → SMS Messages | One-to-Many | User can analyze multiple SMS |
| User → Feedback | One-to-Many | User provides feedback on predictions |
| SMS → Feedback | One-to-Many | SMS can receive feedback from users |
| Campaigns | Independent | Derived from clustered SMS messages |
