from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from sms_analysis.models import SMSMessage

from .assistant import generate_chat_response
from .llm_service import is_llm_configured


class ChatView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user_message = (request.data.get('message') or '').strip()
        sms_id = request.data.get('sms_id')
        history = request.data.get('history') or []

        if not user_message:
            return Response({'error': 'Message is required.'}, status=status.HTTP_400_BAD_REQUEST)

        context = {}
        if sms_id:
            try:
                sms = SMSMessage.objects.get(pk=sms_id)
                context = {
                    'message': sms.message,
                    'original_message': sms.message,
                    'prediction': sms.prediction,
                    'confidence': sms.confidence,
                    'reasons': sms.explanation.get('reasons', []) if sms.explanation else [],
                    'fraud_type': sms.fraud_type,
                    'phishing_analysis': sms.phishing_analysis or {},
                    'security_score': sms.security_score,
                    'suspicious_words': sms.suspicious_words or [],
                    'xai_summary': (sms.xai_data or {}).get('summary', ''),
                }
            except SMSMessage.DoesNotExist:
                pass

        response = generate_chat_response(user_message, context, history)
        response['llm_enabled'] = is_llm_configured()
        return Response(response, status=status.HTTP_200_OK)


class ChatStatusView(APIView):
    """Check if LLM is configured for full AI chat."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        import os
        provider = os.getenv('LLM_PROVIDER', 'gemini')
        has_gemini = bool(os.getenv('GEMINI_API_KEY'))
        has_openai = bool(os.getenv('OPENAI_API_KEY'))
        return Response({
            'llm_enabled': is_llm_configured(),
            'provider': provider if is_llm_configured() else None,
            'gemini_configured': has_gemini,
            'openai_configured': has_openai,
        })
