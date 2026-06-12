from django.contrib import admin

from .models import Feedback, SMSMessage

admin.site.register(SMSMessage)
admin.site.register(Feedback)
