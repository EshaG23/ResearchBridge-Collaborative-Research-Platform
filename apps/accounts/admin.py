from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "is_staff", "is_demo", "date_joined")
    search_fields = ("email",)
    list_filter = ("is_active", "is_staff", "is_demo")
    fields = ("email", "is_active", "is_staff", "is_demo", "email_verified_at", "date_joined")
    readonly_fields = ("email", "is_demo", "email_verified_at", "date_joined")

    def has_add_permission(self, request):
        # Accounts will be created by OTP verification; admins use createsuperuser.
        return False
