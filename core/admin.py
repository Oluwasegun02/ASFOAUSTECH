from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Leader, AboutContent, PrayerRequest, ContactMessage, Event, Profile, Alumni, Resource, Blog, Mentor, Comment, DailyInspiration

User = get_user_model()

class AlumniAdminForm(forms.ModelForm):
    # Override achievements to use a Textarea instead of the default JSON editor
    achievements = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Enter each achievement on a new line'}),
        required=False,
        help_text="Enter each achievement on a new line."
    )

    class Meta:
        model = Alumni
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert the list back into a newline-separated string for the editor
        if self.instance and isinstance(self.instance.achievements, list):
            self.initial['achievements'] = "\n".join(self.instance.achievements)

    def clean_achievements(self):
        # Convert the newline-separated string back into a Python list
        data = self.cleaned_data.get('achievements', '')
        return [line.strip() for line in data.splitlines() if line.strip()]

class LeaderAdminForm(forms.ModelForm):
    # Override achievements to use a Textarea instead of the default JSON editor
    achievements = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Enter each achievement on a new line'}),
        required=False,
        help_text="Enter each achievement on a new line."
    )

    class Meta:
        model = Leader
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert the list back into a newline-separated string for the editor
        if self.instance and isinstance(self.instance.achievements, list):
            self.initial['achievements'] = "\n".join(self.instance.achievements)

    def clean_achievements(self):
        # Convert the newline-separated string back into a Python list
        data = self.cleaned_data.get('achievements', '')
        return [line.strip() for line in data.splitlines() if line.strip()]

class FellowshipAdminSite(admin.AdminSite):
    site_header = "ASF OAUSTECH Admin"
    site_title = "Fellowship Portal"
    index_title = "Management Console"

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['stats'] = {
            'leaders': Leader.objects.count(),
            'events': Event.objects.count(),
            'mentors': Mentor.objects.count(),
            'alumni': Alumni.objects.count(),
            'blogs': Blog.objects.count(),
            'users': User.objects.count(),
            'pending_prayers': PrayerRequest.objects.filter(status='pending').count(),
            'unread_messages': ContactMessage.objects.filter(is_read=False).count(),
        }
        return super().index(request, extra_context)

admin_site = FellowshipAdminSite(name='fellowship_admin')

@admin.register(Leader, site=admin_site)
class LeaderAdmin(admin.ModelAdmin):
    form = LeaderAdminForm
    list_display = ('name', 'role', 'order', 'image_preview', 'linkedin_url', 'twitter_url', 'whatsapp_url')
    list_editable = ('order',)
    search_fields = ('name', 'role', 'bio')

    def image_preview(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html('<img src="{}" style="width: 45px; height:45px; border-radius: 50%; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'

@admin.register(Mentor, site=admin_site)
class MentorAdmin(admin.ModelAdmin):
    form = LeaderAdminForm
    list_display = ('name', 'role', 'specialization', 'order', 'image_preview', 'linkedin_url', 'facebook_url', 'email')
    list_editable = ('order',)

    def image_preview(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html('<img src="{}" style="width: 45px; height:45px; border-radius: 50%; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'

@admin.register(Event, site=admin_site)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'location', 'registered_count')

@admin.register(Alumni, site=admin_site)
class AlumniAdmin(admin.ModelAdmin):
    form = AlumniAdminForm # Use the new form for Alumni
    list_display = ('name', 'degree', 'location', 'profile_picture_preview', 'linkedin_url', 'twitter_url', 'facebook_url')
    search_fields = ('name', 'degree', 'location', 'description')

    def profile_picture_preview(self, obj):
        from django.utils.html import format_html
        if obj.profile_picture:
            return format_html('<img src="{}" style="width: 45px; height:45px; border-radius: 50%; object-fit: cover;" />', obj.profile_picture.url)
        return "No Image"
    profile_picture_preview.short_description = 'Preview'

@admin.register(Blog, site=admin_site)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'date', 'get_likes_count', 'get_comments_count')
    search_fields = ('title', 'author', 'excerpt')
    list_filter = ('category', 'date')

    def get_likes_count(self, obj):
        return obj.liked_by.count()
    get_likes_count.short_description = 'Likes'

    def get_comments_count(self, obj):
        return obj.comments.count()
    get_comments_count.short_description = 'Comments'

@admin.register(DailyInspiration, site=admin_site)
class DailyInspirationAdmin(admin.ModelAdmin):
    list_display = ('verse', 'created_at')

@admin.register(Resource, site=admin_site)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'link')
    list_filter = ('type',)

@admin.register(AboutContent, site=admin_site)
class AboutContentAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Keep only one About section
        return not AboutContent.objects.exists()

@admin.register(PrayerRequest, site=admin_site)
class PrayerRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_at', 'is_private')
    list_filter = ('status', 'is_private', 'created_at')
    actions = ['mark_as_prayed']

    @admin.action(description='Mark selected requests as Prayed For')
    def mark_as_prayed(self, request, queryset):
        queryset.update(status='prayed')

@admin.register(ContactMessage, site=admin_site)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    actions = ['mark_as_read']

    @admin.action(description='Mark selected messages as Read')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

# Inline admin for Profile to show it on the User admin page
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

# Re-register UserAdmin
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

@admin.register(User, site=admin_site)
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_department', 'get_phone_number')

    def get_department(self, obj):
        return obj.profile.department if hasattr(obj, 'profile') else ''
    get_department.short_description = 'Department'

    def get_phone_number(self, obj):
        return obj.profile.phone_number if hasattr(obj, 'profile') else ''
    get_phone_number.short_description = 'Phone Number'