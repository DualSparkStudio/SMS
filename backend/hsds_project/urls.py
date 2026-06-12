"""TextGuard URL Configuration."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/sms/', include('sms_analysis.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/campaigns/', include('campaigns.urls')),
    path('api/chat/', include('chatbot.urls')),
    path('api/ml/', include('ml_engine.urls')),
]
