"""Comprehensive system test for TextGuard platform."""
import json
import sys
import urllib.request
import urllib.error

BASE = "http://localhost:8000/api"

def req(method, path, data=None, token=None):
    url = f"{BASE}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode()) if e.read() else {"error": str(e)}


def test_sms_cases():
    cases = [
        {
            "name": "Lottery Spam (EN)",
            "message": "Congratulations! You won Rs 50000. Click here to claim your reward.",
            "expected": "spam",
        },
        {
            "name": "Normal SMS (HAM)",
            "message": "Hey, are we still meeting for lunch tomorrow at 1pm?",
            "expected": "ham",
        },
        {
            "name": "Banking Fraud",
            "message": "URGENT: Your SBI account will be blocked. Verify OTP immediately at http://sbi-secure-kyc.xyz",
            "expected": "spam",
        },
        {
            "name": "Job Scam",
            "message": "Earn Rs 5000 per day work from home. No experience needed. WhatsApp now.",
            "expected": "spam",
        },
        {
            "name": "Investment Scam",
            "message": "Double your money in 7 days. Guaranteed 200% returns. Invest now.",
            "expected": "spam",
        },
        {
            "name": "Legitimate OTP",
            "message": "Your OTP for transaction is 482910. Valid for 10 minutes.",
            "expected": "ham",
        },
        {
            "name": "Hindi Spam",
            "message": "आप इनाम जीत चुके हैं। अभी क्लिक करें और अपना पुरस्कार प्राप्त करें।",
            "expected": "spam",
        },
        {
            "name": "Marathi Spam",
            "message": "तुम्ही बक्षीस जिंकले आहे. त्वरित क्लिक करा आणि बक्षीस मिळवा.",
            "expected": "spam",
        },
        {
            "name": "Birthday (HAM)",
            "message": "Happy birthday! Hope you have a wonderful day.",
            "expected": "ham",
        },
        {
            "name": "Phishing URL only context",
            "message": "Verify your account at paypal-security-login.xyz immediately",
            "expected": "spam",
        },
    ]

    results = []
    for c in cases:
        status, data = req("POST", "/sms/analyze/", {"message": c["message"]})
        if status != 201:
            results.append({**c, "pass": False, "error": data, "actual": None})
            continue
        actual = data.get("prediction")
        correct = actual == c["expected"]
        results.append({
            **c,
            "pass": correct,
            "actual": actual,
            "confidence": data.get("confidence"),
            "fraud_type": data.get("fraud_type"),
            "security_score": data.get("security_score"),
            "language": data.get("language"),
            "phishing_risk": data.get("phishing_analysis", {}).get("max_risk", 0),
            "sms_id": data.get("id"),
        })
    return results


def main():
    report = {"modules": {}, "prediction_accuracy": None, "issues": []}

    # 1. Chat status
    s, d = req("GET", "/chat/status/")
    report["modules"]["chat_status"] = s == 200 and d.get("llm_enabled")

    # 2. Dashboard
    s, d = req("GET", "/analytics/dashboard/")
    report["modules"]["dashboard"] = s == 200 and "spam_vs_ham" in d

    # 3. Model comparison
    s, d = req("GET", "/ml/comparison/")
    report["modules"]["ml_comparison"] = s == 200 and "comparison" in d
    if s == 200:
        report["model_metrics"] = d.get("comparison", [])

    # 4. Campaigns list
    s, d = req("GET", "/campaigns/")
    report["modules"]["campaigns"] = s == 200

    # 5. SMS prediction tests
    sms_results = test_sms_cases()
    passed = sum(1 for r in sms_results if r.get("pass"))
    total = len(sms_results)
    report["prediction_accuracy"] = {
        "passed": passed,
        "total": total,
        "percent": round(passed / total * 100, 1) if total else 0,
        "details": sms_results,
    }

    # 6. Chat LLM
    s, d = req("POST", "/chat/", {"message": "What is smishing?", "history": []})
    report["modules"]["chat_llm"] = s == 200 and d.get("provider") == "gemini" and len(d.get("reply", "")) > 50

    # 7. Chat with SMS context
    spam_id = next((r["sms_id"] for r in sms_results if r.get("sms_id")), None)
    if spam_id:
        s, d = req("POST", "/chat/", {"message": "Why is this dangerous?", "sms_id": spam_id, "history": []})
        report["modules"]["chat_context"] = s == 200 and len(d.get("reply", "")) > 30

    # 8. Auth register + login
    import random
    email = f"testuser{random.randint(10000,99999)}@test.com"
    s, d = req("POST", "/auth/register/", {
        "username": f"test{random.randint(1000,9999)}",
        "email": email,
        "first_name": "Test",
        "password": "testpass123",
        "password_confirm": "testpass123",
    })
    report["modules"]["auth_register"] = s == 201
    s, d = req("POST", "/auth/login/", {"email": email, "password": "testpass123"})
    token = d.get("access") if s == 200 else None
    report["modules"]["auth_login"] = bool(token)

    # 9. Feedback (needs auth)
    if token and spam_id:
        s, d = req("POST", "/sms/feedback/", {"sms_id": spam_id, "feedback": "correct"}, token=token)
        report["modules"]["feedback"] = s in (200, 201)

    # 10. Learning dashboard
    s, d = req("GET", "/analytics/learning/")
    report["modules"]["learning_dashboard"] = s == 200

    # Identify issues
    for mod, ok in report["modules"].items():
        if not ok:
            report["issues"].append(f"Module failed: {mod}")

    wrong_preds = [r for r in sms_results if not r.get("pass")]
    for r in wrong_preds:
        report["issues"].append(
            f"Wrong prediction: {r['name']} - expected {r['expected']}, got {r.get('actual')}"
        )

    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
