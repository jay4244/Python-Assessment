from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from django.utils.http import url_has_allowed_host_and_scheme

from .decorators import author_or_admin_required, role_required
from .forms import CategoryForm, CommentForm, LoginForm, PostForm, RegisterForm
from .models import Category, Comment, Follow, Like, Post, User


def register_view(request):
    if request.user.is_authenticated:
        return redirect("post_list")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Registration successful.")
        next_url = request.GET.get("next") or request.POST.get("next")
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect("post_list")
    if request.method == "POST":
        messages.error(request, "Please correct the errors below.")
    return render(request, "auth/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("post_list")

    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        messages.success(request, "Logged in successfully.")
        next_url = request.GET.get("next") or request.POST.get("next")
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect("post_list")
    if request.method == "POST":
        messages.error(request, "Invalid username or password.")
    return render(request, "auth/login.html", {"form": form, "next": request.GET.get("next", "")})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect("login")


@login_required
def post_list(request):
    posts = (
        Post.objects.select_related("author", "category")
        .prefetch_related("tags")
        .annotate(total_comments=Count("comments", distinct=True), total_likes=Count("likes", distinct=True))
    )
    category_id = request.GET.get("category")
    author_id = request.GET.get("author")
    date_value = request.GET.get("date")

    if category_id:
        posts = posts.filter(category_id=category_id)
    if author_id:
        posts = posts.filter(author_id=author_id)
    if date_value:
        parsed_date = parse_date(date_value)
        if parsed_date:
            posts = posts.filter(created_at__date=parsed_date)
        else:
            messages.error(request, "Invalid date filter format. Use YYYY-MM-DD.")

    context = {
        "posts": posts,
        "categories": Category.objects.all(),
        "authors": User.objects.filter(posts__isnull=False).distinct().order_by("username"),
        "selected_category": category_id or "",
        "selected_author": author_id or "",
        "selected_date": date_value or "",
    }
    return render(request, "posts/post_list.html", context)


@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related("author", "category").prefetch_related("tags"), pk=pk)
    comments = post.comments.select_related("user")
    has_liked = Like.objects.filter(post=post, user=request.user).exists()
    is_following = False
    if request.user != post.author:
        is_following = Follow.objects.filter(follower=request.user, following=post.author).exists()

    form = CommentForm()

    return render(
        request,
        "posts/post_detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_form": form,
            "has_liked": has_liked,
            "total_likes": post.likes.count(),
            "is_following": is_following,
        },
    )


@login_required
def add_comment(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.post = post
        comment.save()
        messages.success(request, "Comment added.")
    else:
        messages.error(request, "Please write a valid comment.")
    return redirect("post_detail", pk=pk)


@login_required
@author_or_admin_required
def create_post(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        form.save_m2m()
        messages.success(request, "Post created successfully.")
        return redirect("post_detail", pk=post.pk)
    return render(request, "posts/post_form.html", {"form": form, "title": "Create Post"})


@login_required
def add_category(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully.")
            return redirect("create_post")
        messages.error(request, "Could not add category. Please fix the errors below.")
    return render(request, "categories/add_category.html", {"form": form})


@login_required
@author_or_admin_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author and request.user.role != User.Role.ADMIN:
        return HttpResponseForbidden("You cannot edit this post.")

    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Post updated successfully.")
        return redirect("post_detail", pk=post.pk)
    return render(request, "posts/post_form.html", {"form": form, "title": "Edit Post"})


@login_required
@author_or_admin_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author and request.user.role != User.Role.ADMIN:
        return HttpResponseForbidden("You cannot delete this post.")

    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted.")
        return redirect("post_list")
    return render(request, "posts/post_confirm_delete.html", {"post": post})


@login_required
def toggle_like(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
        messages.info(request, "Post unliked.")
    else:
        messages.success(request, "Post liked.")
    return redirect("post_detail", pk=pk)


@login_required
def edit_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user != comment.user:
        return HttpResponseForbidden("You cannot edit this comment.")

    form = CommentForm(request.POST or None, instance=comment)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Comment updated.")
        return redirect("post_detail", pk=comment.post.pk)
    return render(request, "comments/comment_form.html", {"form": form, "comment": comment})


@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user != comment.user:
        return HttpResponseForbidden("You cannot delete this comment.")

    post_pk = comment.post.pk
    if request.method == "POST":
        comment.delete()
        messages.success(request, "Comment deleted.")
        return redirect("post_detail", pk=post_pk)
    return render(request, "comments/comment_confirm_delete.html", {"comment": comment})


@login_required
def toggle_follow(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    if target_user == request.user:
        messages.error(request, "You cannot follow yourself.")
        return redirect("user_profile", user_id=user_id)

    follow, created = Follow.objects.get_or_create(follower=request.user, following=target_user)
    if not created:
        follow.delete()
        messages.info(request, f"You unfollowed {target_user.username}.")
    else:
        messages.success(request, f"You are now following {target_user.username}.")
    return redirect("user_profile", user_id=user_id)


@login_required
def user_profile(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    posts = profile_user.posts.select_related("category").prefetch_related("tags")
    is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    return render(
        request,
        "users/profile.html",
        {
            "profile_user": profile_user,
            "posts": posts,
            "is_following": is_following,
        },
    )


@login_required
@role_required([User.Role.ADMIN])
def admin_dashboard(request):
    context = {
        "users_count": User.objects.count(),
        "posts_count": Post.objects.count(),
        "comments_count": Comment.objects.count(),
        "categories": Category.objects.annotate(post_count=Count("posts")).order_by("-post_count"),
        "latest_users": User.objects.order_by("-date_joined")[:5],
        "latest_posts": Post.objects.select_related("author").order_by("-created_at")[:5],
    }
    return render(request, "dashboard/admin_dashboard.html", context)
