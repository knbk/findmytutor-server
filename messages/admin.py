from django.contrib import admin

from .models import Message, MessageThread


admin.site.register([Message, MessageThread])
