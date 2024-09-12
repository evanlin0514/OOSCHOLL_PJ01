from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('name', 'email', 'password1', 'password2')

class LoginForm(forms.Form):
    email = forms.EmailField(max_length=200)
    password = forms.CharField(widget=forms.PasswordInput)