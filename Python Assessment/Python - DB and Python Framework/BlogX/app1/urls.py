from django.urls import path

from . import views

urlpatterns = [
    # Auth
    path("", views.post_list, name="post_list"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Blog CRUD
    path("posts/create/", views.create_post, name="create_post"),
    path("categories/add/", views.add_category, name="add_category"),
    path("posts/<int:pk>/", views.post_detail, name="post_detail"),
    path("posts/<int:pk>/edit/", views.edit_post, name="edit_post"),
    path("posts/<int:pk>/delete/", views.delete_post, name="delete_post"),

    # Like / Unlike
    path("posts/<int:pk>/toggle-like/", views.toggle_like, name="toggle_like"),

    # Comments
    path("posts/<int:pk>/comments/add/", views.add_comment, name="add_comment"),
    path("comments/<int:pk>/edit/", views.edit_comment, name="edit_comment"),
    path("comments/<int:pk>/delete/", views.delete_comment, name="delete_comment"),

    # Follow system
    path("users/<int:user_id>/toggle-follow/", views.toggle_follow, name="toggle_follow"),
    path("users/<int:user_id>/", views.user_profile, name="user_profile"),

    # Dashboard
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
]
