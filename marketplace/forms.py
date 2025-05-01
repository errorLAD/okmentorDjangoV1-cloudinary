from django import forms
from django.contrib.auth.models import User
from .models import MentorProfile, Service, AvailabilitySlot, DigitalProduct


class MenteeSignupForm(forms.ModelForm):
    name = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.first_name = self.cleaned_data['name']
        if commit:
            user.save()
        return user

class AvailabilitySlotForm(forms.ModelForm):
    class Meta:
        model = AvailabilitySlot
        fields = ['start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration_minutes', 'price']

class DigitalProductForm(forms.ModelForm):
    class Meta:
        model = DigitalProduct
        fields = ['name', 'description', 'price', 'file', 'delivery_instructions']

class MentorSignupForm(forms.ModelForm):
    name = forms.CharField(max_length=150, required=True)
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    expertise_tags = forms.CharField(help_text="Comma-separated tags")
    domains = forms.CharField(help_text="Comma-separated domains (tech, marketing, etc.)")
    linkedin_url = forms.URLField(required=False)
    profile_image = forms.ImageField(required=False)
    category = forms.CharField(max_length=100, required=False)

    class Meta:
        model = MentorProfile
        fields = ['name', 'bio', 'expertise_tags', 'domains', 'linkedin_url', 'profile_image', 'category']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        user.first_name = self.cleaned_data['name']
        user.save()
        profile = super().save(commit=False)
        profile.user = user
        profile.is_mentor = True
        if commit:
            profile.save()
        return user

class MentorProfileForm(forms.ModelForm):
    """Form for updating mentor profile information."""
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)
    expertise_tags = forms.CharField(help_text="Comma-separated tags", required=False)
    domains = forms.CharField(help_text="Comma-separated domains (tech, marketing, etc.)", required=False)
    linkedin_url = forms.URLField(required=False)
    profile_image = forms.ImageField(required=False)
    category = forms.CharField(max_length=100, required=False)

    class Meta:
        model = MentorProfile
        fields = ['bio', 'expertise_tags', 'domains', 'linkedin_url', 'profile_image', 'category']
