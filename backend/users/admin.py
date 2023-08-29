from django.contrib import admin

from .models import CustomUser, Subscription


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'role')
    search_fields = ('username',)
    list_filter = ('username', 'email', 'role')
    empty_value_display = '-пусто-'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'author')
    empty_value_display = '-пусто-'
