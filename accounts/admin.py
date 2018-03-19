from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Profile, Tutor, Student, Location


admin.site.register([Profile, Tutor, Student, Location])
admin.site.register(User, UserAdmin)
