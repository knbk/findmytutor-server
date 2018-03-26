from django.contrib import admin

from .models import Meeting, Review

admin.site.register([Meeting, Review])
