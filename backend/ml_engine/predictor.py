"""ML prediction engine with ensemble and fallback."""

import json
import re
from pathlib import Path

import joblib
import numpy as np
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

SPAM_KEYWORDS = [
    'free', 'win', 'winner', 'prize', 'cash', 'urgent', 'congratulations',
    'claim', 'click', 'offer', 'limited', 'lottery', 'reward', 'verify',
    'account', 'blocked', 'otp', 'kyc', 'call now', 'act now', 'expire',
    'gift', 'bonus', 'discount', 'deal', 'promo', 'subscription',
]

MODEL_PATH = settings.ML_MODELS_DIR / 'ensemble_model.joblib'
VECTORIZER_PATH = settings.ML_MODELS_DIR / 'tfidf_vectorizer.joblib'
METRICS_PATH = settings.ML_MODELS_DIR / 'model_metrics.json'


def _preprocess(text: str) -> str:
    text = text.lower()
    text = re.sub(r'http\S+|www\.\S+', ' url_link ', text)
    text = re.sub(r'[^a-zA-Z0-9\s₹]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _keyword_score(text: str) -> float:
    text_lower = text.lower()
    matches = sum(1 for kw in SPAM_KEYWORDS if kw in text_lower)
    return min(matches / 5.0, 1.0)


class SMSPredictor:
    """Hybrid ML predictor with trained model or rule-based fallback."""

    def __init__(self):
        self.model = None
        self.vectorizer = None
        self._load_models()

    def _load_models(self):
        try:
            if MODEL_PATH.exists() and VECTORIZER_PATH.exists():
                self.model = joblib.load(MODEL_PATH)
                self.vectorizer = joblib.load(VECTORIZER_PATH)
        except Exception:
            self.model = None
            self.vectorizer = None

    def predict(self, text: str) -> dict:
        processed = _preprocess(text)
        keyword_prob = _keyword_score(text)

        if self.model and self.vectorizer:
            try:
                X = self.vectorizer.transform([processed])
                proba = self.model.predict_proba(X)[0]
                spam_prob = float(proba[1]) if len(proba) > 1 else float(proba[0])
            except Exception:
                spam_prob = keyword_prob
        else:
            spam_prob = keyword_prob

        combined_prob = 0.7 * spam_prob + 0.3 * keyword_prob
        prediction = 'spam' if combined_prob >= 0.5 else 'ham'
        confidence = combined_prob if prediction == 'spam' else 1 - combined_prob

        return {
            'prediction': prediction,
            'confidence': round(confidence, 4),
            'spam_probability': round(combined_prob, 4),
            'model_used': 'ensemble' if self.model else 'rule_based',
        }

    @staticmethod
    def get_metrics() -> dict:
        if METRICS_PATH.exists():
            with open(METRICS_PATH) as f:
                return json.load(f)
        return {}


def get_default_training_data():
    """Built-in training dataset for initial model training."""
    spam_samples = [
        "Congratulations! You won Rs 50000. Click here to claim your reward.",
        "URGENT: Your bank account will be blocked. Verify OTP immediately.",
        "Free iPhone! You are selected winner. Call now to claim prize.",
        "Earn Rs 5000 per day work from home. No experience needed. WhatsApp now.",
        "Double your money in 7 days. Guaranteed 200% returns. Invest now.",
        "Your KYC is pending. Update immediately or account will be suspended.",
        "Dear customer, your SBI account has been locked. Click link to verify.",
        "You have won a lottery of 10 lakh rupees. Contact us to claim.",
        "Limited offer! Get free recharge. Click www.fake-reward.xyz",
        "Account blocked due to suspicious activity. Share OTP to unlock.",
        "Get rich quick! Forex trading scheme with daily profit.",
        "Amazon free gift waiting for you. Claim at amazon-freegift.xyz",
        "Paypal security alert. Verify login at paypal-security-login.xyz",
        "Congratulations winner! Rs 25000 cashback credited. Claim now.",
        "Work from home job. Daily income Rs 3000. Register today.",
        "Your mobile number won 1 crore in lucky draw. Call this number.",
        "Urgent! Last chance to claim your prize before expiry tonight.",
        "Free Netflix subscription for 1 year. Click to activate now.",
        "Bank KYC update required. Failure to update will close account.",
        "Investment opportunity: 50% monthly returns guaranteed.",
        "Dear your drop for Account 8983784848 Transfer Received Rs 3850 Amount available in your wallet Check now bit.ly/wallet-scam",
    ]
    ham_samples = [
        "Hey, are we still meeting for lunch tomorrow at 1pm?",
        "Your OTP for transaction is 482910. Valid for 10 minutes.",
        "Mom called, she will be home by evening.",
        "Meeting rescheduled to Friday 3pm. Please confirm attendance.",
        "Happy birthday! Hope you have a wonderful day.",
        "The package has been delivered. Please check your doorstep.",
        "Reminder: Doctor appointment on Monday at 10am.",
        "Can you pick up milk on your way home?",
        "Project submission deadline extended to next week.",
        "Thanks for your payment of Rs 1500. Receipt attached.",
        "Class cancelled today due to rain. Will inform new schedule.",
        "Your order #4521 has been shipped. Track at official site.",
        "Good morning! Traffic is heavy on highway, leave early.",
        "Please review the document I shared yesterday.",
        "Dinner at 8pm tonight. Let me know if you can make it.",
        "Your electricity bill of Rs 2340 is due on 15th.",
        "Flight delayed by 2 hours. New departure time 6pm.",
        "Library book due date is tomorrow. Please return on time.",
        "Team outing planned for Saturday. Confirm your availability.",
        "Weather forecast shows rain tomorrow. Carry umbrella.",
    ]
    texts = spam_samples + ham_samples
    labels = [1] * len(spam_samples) + [0] * len(ham_samples)
    return texts, labels
