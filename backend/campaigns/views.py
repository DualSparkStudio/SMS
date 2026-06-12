from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .clustering import detect_campaigns
from .models import Campaign
from .serializers import CampaignSerializer


class CampaignListView(generics.ListAPIView):
    serializer_class = CampaignSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        detect_campaigns()
        return Campaign.objects.filter(is_active=True)


class DetectCampaignsView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        campaigns = detect_campaigns()
        return Response({
            'detected': len(campaigns),
            'campaigns': CampaignSerializer(campaigns, many=True).data,
        }, status=status.HTTP_200_OK)
