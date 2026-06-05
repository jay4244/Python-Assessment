from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Category, Comment, Follow, Like, Post, Tag, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    ordering = ("username",)
    fieldsets = UserAdmin.fieldsets + (
        ("Extra", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Extra", {"fields": ("email", "role")}),
    )
    list_display = ("username", "email", "role", "is_staff", "is_active", "date_joined")
    list_filter = ("role", "is_staff", "is_superuser", "is_active", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "created_at", "updated_at")
    list_filter = ("category", "author__role", "created_at", "updated_at")
    search_fields = ("title", "content", "author__username")
    filter_horizontal = ("tags",)
    autocomplete_fields = ("author", "category")
    date_hierarchy = "created_at"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "created_at")
    list_filter = ("created_at", "user__role")
    search_fields = ("content", "user__username", "post__title")
    autocomplete_fields = ("post", "user")
    date_hierarchy = "created_at"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "post")
    list_filter = ("user__role", "post__category")
    search_fields = ("user__username", "post__title")
    autocomplete_fields = ("user", "post")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "following")
    list_filter = ("follower__role", "following__role")
    search_fields = ("follower__username", "following__username")
    autocomplete_fields = ("follower", "following")

