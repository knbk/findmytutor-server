from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Tutor, Student, Location


admin.site.register([Tutor, Student, Location])
admin.site.register(User, UserAdmin)
