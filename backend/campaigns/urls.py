from django.urls import path

from .views import CampaignListView, DetectCampaignsView

urlpatterns = [
    path('', CampaignListView.as_view(), name='campaign_list'),
    path('detect/', DetectCampaignsView.as_view(), name='detect_campaigns'),
]
