from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Alumni, Resource, Comment

class CustomUserCreationForm(UserCreationForm):
    member_type = forms.ChoiceField(choices=Profile.MEMBER_TYPES, required=True, label="I am a...")
    department = forms.CharField(max_length=100, required=False, help_text="Your academic department (e.g., Computer Science)")
    phone_number = forms.CharField(max_length=20, required=False, help_text="Your phone number (optional)")

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',) # Add email to default fields if not already there

    def save(self, commit=True):
        user = super().save(commit=False)
        # Ensure email is saved if it's part of the form
        if 'email' in self.cleaned_data:
            user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile = Profile.objects.create(
                user=user,
                member_type=self.cleaned_data.get('member_type'),
                department=self.cleaned_data.get('department'),
                phone_number=self.cleaned_data.get('phone_number')
            )
            profile.save()
        return user

class AlumniProfileForm(forms.ModelForm):
    achievements_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter each achievement on a new line'}),
        required=False,
        label="Key Achievements"
    )

    class Meta:
        model = Alumni
        fields = ['name', 'title', 'degree', 'location', 'description', 'profile_picture', 'linkedin_url', 'twitter_url', 'facebook_url']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and isinstance(self.instance.achievements, list):
            self.initial['achievements_text'] = "\n".join(self.instance.achievements)

    def save(self, commit=True):
        instance = super().save(commit=False)
        data = self.cleaned_data.get('achievements_text', '')
        instance.achievements = [line.strip() for line in data.splitlines() if line.strip()]
        if commit:
            instance.save()
        return instance

class ResourceSuggestionForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'type', 'description', 'link']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Write a comment...'}),
        }
        labels = {
            'text': '',
        }