from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Category, Comment, Post, User


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "role", "password1", "password2")


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Username"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password"}))


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "content", "cover_image", "category", "tags")
        widgets = {
            "content": forms.Textarea(attrs={"rows": 6}),
            "tags": forms.SelectMultiple(attrs={"size": 5}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content",)
        widgets = {
            "content": forms.Textarea(attrs={"rows": 3, "placeholder": "Write your comment..."}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name",)
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Enter category name"}),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if Category.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("This category already exists.")
        return name
