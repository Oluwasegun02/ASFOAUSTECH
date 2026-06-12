from django.db import models
from django.contrib.auth.models import User
from django_ckeditor_5.fields import CKEditor5Field

class Leader(models.Model):
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='leadership/', null=True, blank=True)
    achievements = models.JSONField(default=list, blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Order in which they appear on the site")
    is_current = models.BooleanField(default=True, help_text="Uncheck to move to Past Excos")
    tenure = models.CharField(max_length=50, default="2024/2025", help_text="Group year (e.g. 2023/2024)")
    linkedin_url = models.URLField(blank=True, null=True, verbose_name="LinkedIn URL")
    twitter_url = models.URLField(blank=True, null=True, verbose_name="X (Twitter) URL")
    whatsapp_url = models.URLField(blank=True, null=True, verbose_name="WhatsApp Link (wa.me)")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

class AboutContent(models.Model):
    title = models.CharField(max_length=255, default="About Our Fellowship")
    history = models.TextField()
    vision = models.TextField()
    mission = models.TextField()
    featured_image = models.ImageField(upload_to='about/', blank=True, null=True)

    def __str__(self):
        return self.title

class Profile(models.Model):
    MEMBER_TYPES = [
        ('student', 'Student'),
        ('alumni', 'Alumni'),
        ('online', 'Online Member'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    member_type = models.CharField(max_length=20, choices=MEMBER_TYPES, default='student')
    department = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    skills = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class Mentor(models.Model):
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255, help_text="e.g. Career Mentor, Spiritual Father")
    specialization = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='mentors/', null=True, blank=True)
    achievements = models.JSONField(default=list, blank=True)
    order = models.PositiveIntegerField(default=0)
    linkedin_url = models.URLField(blank=True, null=True, verbose_name="LinkedIn URL")
    twitter_url = models.URLField(blank=True, null=True, verbose_name="X (Twitter) URL")
    facebook_url = models.URLField(blank=True, null=True, verbose_name="Facebook URL")
    email = models.EmailField(blank=True, null=True, verbose_name="Email Address")
    whatsapp_url = models.URLField(blank=True, null=True, verbose_name="WhatsApp Link")

    def __str__(self):
        return self.name

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField(default=100)
    flyer = models.ImageField(upload_to='event_flyers/', null=True, blank=True)
    registered_users = models.ManyToManyField('auth.User', related_name='registered_events', blank=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return self.title

    @property
    def registered_count(self):
        return self.registered_users.count()

    @property
    def remaining_time(self):
        from django.utils import timezone
        import datetime
        event_dt = datetime.datetime.combine(self.date, self.time)
        now = datetime.datetime.now()
        if event_dt > now:
            diff = event_dt - now
            if diff.days > 0:
                return f"{diff.days} days left"
            return f"{diff.seconds // 3600} hours left"
        return "Ongoing or Concluded"

class Alumni(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='alumni_profile')
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, help_text="Current professional role")
    degree = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField()
    achievements = models.JSONField(default=list, blank=True)
    profile_picture = models.ImageField(upload_to='alumni_profiles/', null=True, blank=True)
    linkedin_url = models.URLField(blank=True, null=True, verbose_name="LinkedIn Profile URL")
    twitter_url = models.URLField(blank=True, null=True, verbose_name="X (Twitter) Profile URL")
    facebook_url = models.URLField(blank=True, null=True, verbose_name="Facebook Profile URL")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Resource(models.Model):
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=100, help_text="e.g. Book, Video, Study Guide")
    description = models.TextField()
    link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Blog(models.Model):
    CATEGORIES = [
        ('Testimony', 'Testimony'),
        ('Teaching', 'Teaching'),
        ('News', 'News'),
        ('Event', 'Event'),
    ]
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100)
    date = models.DateField()
    excerpt = models.TextField()
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORIES, default='News')
    content = CKEditor5Field('Content', config_name='extends')
    liked_by = models.ManyToManyField(User, related_name='liked_blogs', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.blog.title}"

class PrayerRequest(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    request = models.TextField()
    category = models.CharField(max_length=100, default="Prayer")
    is_private = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    pray_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('prayed', 'Prayed For'),
        ('archived', 'Archived')
    ], default='pending')

    def __str__(self):
        return f"Request by {self.name} on {self.created_at.date()}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name}: {self.subject}"

class DailyInspiration(models.Model):
    text = models.TextField()
    verse = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.verse}: {self.text[:50]}..."