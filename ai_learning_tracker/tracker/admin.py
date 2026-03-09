from django.contrib import admin
from .models import UserProfile, LearningLog, MotivationalQuote, LearningActivity

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'streak', 'last_log_date', 'total_logs']
    search_fields = ['user__username']

@admin.register(LearningLog)
class LearningLogAdmin(admin.ModelAdmin):
    list_display = ['record_id', 'user', 'title', 'date', 'created_at']
    list_filter = ['date', 'user']
    search_fields = ['record_id', 'title', 'tags', 'notes']
    readonly_fields = ['record_id']

@admin.register(MotivationalQuote)
class MotivationalQuoteAdmin(admin.ModelAdmin):
    list_display = ['text', 'author', 'created_at']
    search_fields = ['text', 'author']

@admin.register(LearningActivity)
class LearningActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'count']
    list_filter = ['date', 'user']
