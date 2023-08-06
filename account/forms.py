from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator


class LoginForm(forms.Form):
    username = forms.CharField(widget= forms.TextInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"})
    )


class SignUpForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"})
    )
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    email = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"})
    )   
    phone_number = forms.CharField(widget=forms.NumberInput(attrs={"class": "form-control", "placeholder":"Enter Safaricom number 07...","type": "tel"}),
                                   validators=[MinLengthValidator(10), MaxLengthValidator(10),RegexValidator(r'^\d{1,10}$')]
    )


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use. Please use a different email address.')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already in use. Please use a different username.')
        return username
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('This phone number is already in use. Please use a different phone number.')
        return phone_number
    
    #ensuring that valid user type is selected
    def clean(self):
        cleaned_data = super().clean()
        is_tenant = cleaned_data.get('is_tenant')
        is_landlord = cleaned_data.get('is_landlord')

        if is_tenant and is_landlord:
            raise forms.ValidationError('You can only select either Tenant or Landlord, not both.')
        elif not is_tenant and not is_landlord:
            raise forms.ValidationError('You must select either Tenant or Landlord.')

    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'is_admin', 'is_tenant', 'is_landlord', 'phone_number')


class UpdateProfileForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(widget=forms.TextInput(attrs={"class": "form-control"}))
    phone_number = forms.CharField(widget=forms.NumberInput(attrs={"class": "form-control", "placeholder":"Enter Safaricom number in format 07xxxxxxxx","type": "tel"}))
    password1 = forms.CharField(label="New password", widget=forms.PasswordInput(attrs={"class": "form-control"}), required=False)
    password2 = forms.CharField(label="New password confirmation", widget=forms.PasswordInput(attrs={"class": "form-control"}), required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_username = self.instance.username
        self.initial_email = self.instance.email
        self.initial_phone_number = self.instance.phone_number

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username != self.initial_username and User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already in use. Please use a different username.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email != self.initial_email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use. Please use a different email address.')
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number != self.initial_phone_number and User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('This phone number is already in use. Please use a different phone number.')
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("The two password fields didn't match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password1 = self.cleaned_data.get('password1')
        if password1:
            user.set_password(password1)
        if commit:
            user.save()
        return user
