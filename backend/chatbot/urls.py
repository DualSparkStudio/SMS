from django.urls import path

from .views import ChatStatusView, ChatView

urlpatterns = [
    path('', ChatView.as_view(), name='chat'),
    path('status/', ChatStatusView.as_view(), name='chat_status'),
]
