"""
Hybrid Adaptive Spam Detection Framework (HASDF)

Proposed dissertation methodology pipeline:
1. SMS Received
2. Language Detection
3. URL Analysis
4. Fraud Pattern Analysis
5. Machine Learning Prediction
6. Explainable AI Layer
7. Security Score Generation
8. Campaign Detection (async via campaigns module)
9. User Feedback Learning
"""

from chatbot.llm_service import classify_sms_with_llm, is_llm_configured

from .fraud_detector import detect_fraud
from .language_detector import detect_language, get_language_name, translate_to_english
from .phishing_detector import analyze_urls_in_text, extract_urls
from .predictor import SMSPredictor
from .security_score import calculate_security_score
from .xai_explainer import find_suspicious_words, generate_xai_explanation


def _apply_rule_overrides(ml_result: dict, phishing: dict, fraud: dict) -> tuple[str, float]:
    """Boost spam detection using URL/fraud signals when ML under-classifies."""
    prediction = ml_result['prediction']
    confidence = ml_result['confidence']
    spam_prob = ml_result['spam_probability']

    if phishing['max_risk'] >= 50 and prediction == 'spam':
        confidence = min(confidence + 0.05, 0.99)
    elif fraud['fraud_type'] and prediction == 'spam':
        confidence = min(confidence + 0.03, 0.99)

    if phishing['max_risk'] >= 50 or fraud['confidence'] >= 0.5:
        if prediction == 'ham':
            prediction = 'spam'
            confidence = max(spam_prob, phishing['max_risk'] / 100, fraud['confidence'], 0.8)

    return prediction, round(confidence, 4)


def _resolve_final_prediction(
    ml_result: dict,
    ai_result: dict | None,
    phishing: dict,
    fraud: dict,
) -> tuple[str, float, str, list[str]]:
    """Merge ML, rule-based, and AI signals into final classification."""
    ml_prediction, ml_confidence = _apply_rule_overrides(ml_result, phishing, fraud)
    ai_reasons: list[str] = []

    if ai_result:
        ai_prediction = ai_result['prediction']
        ai_confidence = ai_result['confidence']
        ai_reasons = ai_result.get('reasons', [])
        provider = ai_result.get('provider', 'ai')

        if ai_prediction == 'spam' and ai_confidence >= 0.55:
            return ai_prediction, ai_confidence, f'ai_{provider}', ai_reasons

        if ai_prediction == 'spam' and ml_prediction == 'spam':
            return 'spam', max(ai_confidence, ml_confidence), f'hybrid_{provider}', ai_reasons

        if ai_prediction == 'ham' and ml_prediction == 'spam' and ml_confidence >= 0.75:
            return ml_prediction, ml_confidence, 'ml_rules', ai_reasons

        if ai_prediction == 'ham' and ai_confidence >= 0.8 and phishing['max_risk'] < 40:
            return ai_prediction, ai_confidence, f'ai_{provider}', ai_reasons

        return ai_prediction, ai_confidence, f'ai_{provider}', ai_reasons

    return ml_prediction, ml_confidence, ml_result['model_used'], ai_reasons


def _should_skip_ai(ml_result: dict, phishing: dict, fraud: dict) -> bool:
    """Skip slow LLM call when rules already produce a confident classification."""
    if not is_llm_configured():
        return True

    prediction, confidence = _apply_rule_overrides(ml_result, phishing, fraud)

    if prediction == 'spam' and confidence >= 0.8:
        if phishing['max_risk'] >= 40 or fraud['confidence'] >= 0.4:
            return True

    if prediction == 'ham' and confidence >= 0.85:
        if phishing['max_risk'] < 20 and not fraud['fraud_type']:
            return True

    return False


class HASDFPipeline:
    """Orchestrates the full HASDF analysis workflow."""

    def __init__(self):
        self.predictor = SMSPredictor()

    def analyze(self, message: str) -> dict:
        pipeline_steps = []

        # Step 1: SMS Received
        pipeline_steps.append({
            'step': 1,
            'name': 'SMS Received',
            'status': 'completed',
            'detail': f'Message length: {len(message)} characters',
        })

        # Step 2: Language Detection
        language = detect_language(message)
        pipeline_steps.append({
            'step': 2,
            'name': 'Language Detection',
            'status': 'completed',
            'detail': f'Detected: {get_language_name(language)} ({language})',
        })

        # Translate for ML if needed
        translated = translate_to_english(message, language)
        analysis_text = translated if language != 'en' else message

        # Step 3: URL Analysis
        phishing = analyze_urls_in_text(message)
        urls = extract_urls(message)
        pipeline_steps.append({
            'step': 3,
            'name': 'URL Analysis',
            'status': 'completed',
            'detail': f'URLs found: {len(urls)}, Risk: {phishing["max_risk"]}%',
        })

        # Step 4: Fraud Pattern Analysis
        fraud = detect_fraud(analysis_text)
        pipeline_steps.append({
            'step': 4,
            'name': 'Fraud Pattern Analysis',
            'status': 'completed',
            'detail': fraud['fraud_label'] or 'No fraud pattern detected',
        })

        # Step 5: ML Prediction
        ml_result = self.predictor.predict(analysis_text)
        pipeline_steps.append({
            'step': 5,
            'name': 'Machine Learning Prediction',
            'status': 'completed',
            'detail': f'{ml_result["prediction"].upper()} ({ml_result["confidence"]:.0%}) via {ml_result["model_used"]}',
        })

        # Step 6: AI Classification (only for ambiguous cases — skips when rules are confident)
        skip_ai = _should_skip_ai(ml_result, phishing, fraud)
        ai_result = None if skip_ai else classify_sms_with_llm(message)
        if ai_result:
            pipeline_steps.append({
                'step': 6,
                'name': 'AI Classification',
                'status': 'completed',
                'detail': (
                    f'{ai_result["prediction"].upper()} ({ai_result["confidence"]:.0%}) '
                    f'via {ai_result.get("provider", "ai")}'
                ),
            })
        elif skip_ai and is_llm_configured():
            rule_pred, rule_conf = _apply_rule_overrides(ml_result, phishing, fraud)
            pipeline_steps.append({
                'step': 6,
                'name': 'AI Classification',
                'status': 'skipped',
                'detail': f'Skipped — high confidence from rules ({rule_pred.upper()} {rule_conf:.0%})',
            })
        else:
            pipeline_steps.append({
                'step': 6,
                'name': 'AI Classification',
                'status': 'skipped' if not is_llm_configured() else 'failed',
                'detail': 'LLM not configured — using ML + rule-based detection' if not is_llm_configured()
                else 'AI classification unavailable — using ML + rule-based detection',
            })

        final_prediction, final_confidence, model_used, ai_reasons = _resolve_final_prediction(
            ml_result, ai_result, phishing, fraud,
        )

        if ai_result and ai_result.get('fraud_type') and not fraud['fraud_label']:
            fraud = {**fraud, 'fraud_label': ai_result['fraud_type'], 'fraud_type': 'ai_detected'}

        # Step 7: Explainable AI
        suspicious = find_suspicious_words(analysis_text)
        xai = generate_xai_explanation(analysis_text, final_prediction, final_confidence)
        if ai_result and ai_result.get('explanation'):
            xai['ai_summary'] = ai_result['explanation']
        pipeline_steps.append({
            'step': 7,
            'name': 'Explainable AI Layer',
            'status': 'completed',
            'detail': f'{len(xai["word_impact_table"])} features analyzed',
        })

        # Step 8: Security Score
        security = calculate_security_score(
            text=analysis_text,
            prediction=final_prediction,
            confidence=final_confidence,
            phishing_risk=phishing['max_risk'],
            fraud_detected=bool(fraud['fraud_label']),
            suspicious_words=suspicious,
        )
        pipeline_steps.append({
            'step': 8,
            'name': 'Security Score Generation',
            'status': 'completed',
            'detail': f'Score: {security["security_score"]}/100 ({security["risk_level"]})',
        })

        # Build explanation reasons
        reasons = list(security['reasons'])
        if ai_reasons:
            reasons = ai_reasons + [r for r in reasons if r not in ai_reasons]
        if fraud['fraud_label']:
            reasons.insert(0, f'Fraud type: {fraud["fraud_label"]}')
        if phishing['urls_found']:
            reasons.append(f'Contains {len(phishing["urls_found"])} URL(s)')
        if ai_result and model_used.startswith(('ai_', 'hybrid_')):
            reasons.insert(0, f'AI-verified classification ({ai_result.get("provider", "llm")})')

        return {
            'prediction': final_prediction,
            'confidence': round(final_confidence, 4),
            'language': language,
            'language_name': get_language_name(language),
            'original_message': message,
            'translated_message': translated if language != 'en' else None,
            'fraud_type': fraud['fraud_label'],
            'fraud_details': fraud,
            'phishing_analysis': phishing,
            'urls_found': urls,
            'suspicious_words': suspicious,
            'security_score': security['security_score'],
            'security_details': security,
            'xai_data': xai,
            'explanation': {
                'reasons': reasons,
                'classification': final_prediction.upper(),
                'confidence_percent': round(final_confidence * 100, 1),
                'model_used': model_used,
            },
            'ai_analysis': ai_result,
            'pipeline_steps': pipeline_steps,
            'framework': 'TextGuard',
        }
