# Testing Documentation

## Test Strategy

| Level | Scope | Tools |
|-------|-------|-------|
| Unit | ML modules, detectors | pytest, Django TestCase |
| Integration | API endpoints | Django REST test client |
| System | Full workflow | Manual + automated |
| ML | Model accuracy | sklearn metrics |

## Manual Test Cases

### TC-01: Spam Detection
| Step | Action | Expected |
|------|--------|----------|
| 1 | Navigate to SMS Detector | Page loads |
| 2 | Enter spam message with "won prize click" | — |
| 3 | Click Analyze | Classification: SPAM, confidence > 80% |

### TC-02: Ham Detection
| Step | Action | Expected |
|------|--------|----------|
| 1 | Enter "Hey, lunch at 1pm?" | — |
| 2 | Analyze | Classification: HAM |

### TC-03: Phishing URL
| Step | Action | Expected |
|------|--------|----------|
| 1 | Enter SMS with `paypal-security-login.xyz` | — |
| 2 | Analyze | URL status: DANGEROUS, risk > 50% |

### TC-04: Multilingual (Hindi)
| Step | Action | Expected |
|------|--------|----------|
| 1 | Enter Hindi spam message | — |
| 2 | Analyze | Language: hi, prediction: spam |

### TC-05: XAI Explanation
| Step | Action | Expected |
|------|--------|----------|
| 1 | Analyze spam message | — |
| 2 | View Results page | Word impact table with High/Medium impacts |

### TC-06: Security Score
| Step | Action | Expected |
|------|--------|----------|
| 1 | Analyze dangerous SMS | Score < 40 (High Risk) |
| 2 | Analyze normal SMS | Score > 70 (Safe) |

### TC-07: User Feedback
| Step | Action | Expected |
|------|--------|----------|
| 1 | Login | JWT token received |
| 2 | Analyze SMS, click "Correct" | Feedback saved |

### TC-08: AI Assistant
| Step | Action | Expected |
|------|--------|----------|
| 1 | Ask "Why is this dangerous?" | Context-aware explanation |

### TC-09: Dashboard
| Step | Action | Expected |
|------|--------|----------|
| 1 | Navigate to Dashboard | Charts render with data |

### TC-10: Model Comparison
| Step | Action | Expected |
|------|--------|----------|
| 1 | Navigate to Research page | Comparison table with 9 models |

## API Testing (curl)

```bash
# Analyze SMS
curl -X POST http://localhost:8000/api/sms/analyze/ \
  -H "Content-Type: application/json" \
  -d '{"message": "You won a prize! Click now!"}'

# Dashboard
curl http://localhost:8000/api/analytics/dashboard/

# Model comparison
curl http://localhost:8000/api/ml/comparison/
```

## ML Model Validation

Target metrics (on test set):
- Accuracy > 98%
- Precision > 97%
- Recall > 97%
- F1 Score > 97%

Run validation:
```bash
cd backend
python manage.py train_models
```

## Performance Testing

| Metric | Target |
|--------|--------|
| API response time | < 2 seconds |
| SMS analysis | < 3 seconds |
| Dashboard load | < 1 second |
