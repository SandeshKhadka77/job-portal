from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

# Forms for user registration and login
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Enter your email'
    }))
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'First name (optional)'
    }))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Last name (optional)'
    }))
# inherited from UserCreationForm and will be customized in the __init__ method for better UI.
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Confirm password'})
        # Remove help text for cleaner UI
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as username
        if commit:
            user.save()
        return user

# Login form for user authentication
class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Enter your email',
        'autocomplete': 'email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Enter your password',
        'autocomplete': 'current-password'
    }))
