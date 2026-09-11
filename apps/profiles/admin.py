from django.contrib import admin
from .models import Department, Skill, ResearchInterest, Profile
admin.site.register([Department, Skill, ResearchInterest])

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user','name','role','teacher_approved','completed_at']
    list_filter = ['role','teacher_approved']
    fields = ['user','name','role','teacher_approved','completed_at']
    readonly_fields = ['user','name','role','completed_at']
    def has_add_permission(self, request):
        return False
