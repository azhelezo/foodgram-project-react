from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from users.models import FollowUser

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('id', 'username', 'first_name', 'email', )
    list_filter = ('username', 'email', )
    empty_value_display = '-пусто-'


class FollowUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author',)
    search_fields = ('user', 'author',)
    list_filter = ('user', 'author',)
    empty_value_display = '-пусто-'


admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
admin.site.register(FollowUser, FollowUserAdmin)
