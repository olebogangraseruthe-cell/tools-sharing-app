from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Tool


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', 'email')


class ToolForm(forms.ModelForm):
    class Meta:
        model = Tool
        fields = ['name', 'category', 'description', 'photo']