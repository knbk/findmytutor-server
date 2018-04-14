from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Tutor, Student, Location, ProfilePicture


admin.site.register([Tutor, Student, Location, ProfilePicture])
admin.site.register(User, UserAdmin)
