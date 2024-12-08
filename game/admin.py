from django.contrib import admin

# Register your models here.
from .models import UserProfile, PlayerStatus, ModeratorPermissions

admin.site.register(UserProfile)
admin.site.register(PlayerStatus)
admin.site.register(ModeratorPermissions)