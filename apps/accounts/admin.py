from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


# Register your models here.
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = (
        "username",
        "email",
        "role",
        "status",
        "grade",
        "is_active",
        "is_staff",
    )
    fieldsets = UserAdmin.fieldsets + (
        ("追加情報", {"fields": ("role", "status", "grade")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("カスタムフィールド", {"fields": ("role",)}),
    )
    list_filter = ("role", "status", "grade")


admin.site.register(CustomUser, CustomUserAdmin)
