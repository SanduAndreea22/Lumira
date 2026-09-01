from django.contrib import admin

from .models import (
    Concern,
    ContactMessage,
    DiagnosticResult,
    Product,
    Routine,
    RoutineStep,
    SkinType,
    UserProfile,
)


@admin.register(Concern)
class ConcernAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "key_ingredient", "order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(SkinType)
class SkinTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "step_time", "price", "is_active")
    list_filter = ("category", "step_time", "is_active", "is_fragrance_free", "is_vegan")
    filter_horizontal = ("concerns", "skin_types")
    search_fields = ("name",)


class RoutineStepInline(admin.TabularInline):
    model = RoutineStep
    extra = 0


@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "is_current", "created_at")
    list_filter = ("is_current",)
    inlines = [RoutineStepInline]


@admin.register(DiagnosticResult)
class DiagnosticResultAdmin(admin.ModelAdmin):
    list_display = ("concern", "skin_type", "experience", "user", "created_at")
    list_filter = ("concern", "skin_type", "experience")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "default_skin_type", "created_at")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at")
    list_filter = ("subject",)
    readonly_fields = ("subject", "name", "email", "message", "created_at")
