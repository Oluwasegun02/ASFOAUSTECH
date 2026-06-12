from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import CustomUserCreationForm, AlumniProfileForm, ResourceSuggestionForm, CommentForm
from .models import Leader, AboutContent, PrayerRequest, ContactMessage, Event, Alumni, Resource, Blog, Profile, Mentor, Comment, DailyInspiration
from .db import repository

def home(request):
    # Now fetching from the SQL database instead of MongoDB for consistency
    events = Event.objects.all()[:3]
    blogs = Blog.objects.all().order_by('-date')[:3]
    inspiration = DailyInspiration.objects.last()
    return render(request, 'home.html', {'events': events, 'blogs': blogs, 'inspiration': inspiration})

@login_required
def events_view(request):
    events = Event.objects.all()
    if request.user.is_authenticated:
        for event in events:
            event.is_registered = event.registered_users.filter(id=request.user.id).exists()
    return render(request, 'events.html', {'events': events})

def register_event(request, event_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to register for events.")
        return redirect('login')
    
    event = get_object_or_404(Event, id=event_id)
    if event.registered_count < event.capacity:
        event.registered_users.add(request.user)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'count': event.registered_count})
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Event full'}, status=400)
            
    return redirect('events')

@login_required
def alumni_view(request):
    alumni = Alumni.objects.all().order_by('-created_at')
    return render(request, 'alumni.html', {'alumni': alumni})

@login_required
def alumni_register(request):
    # Ensure profile exists and check member type
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if profile.member_type != 'alumni':
        messages.warning(request, "This page is specifically for our Alumni members.")
        return redirect('alumni')
        
    instance, created = Alumni.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = AlumniProfileForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Your alumni profile has been updated!")
            return redirect('alumni')
    else:
        form = AlumniProfileForm(instance=instance)
    return render(request, 'alumni_profile_update.html', {'form': form})

@login_required
def blogs_view(request):
    category = request.GET.get('category')
    if category:
        blogs = Blog.objects.filter(category=category).order_by('-date').prefetch_related('comments')
    else:
        blogs = Blog.objects.all().order_by('-date').prefetch_related('comments')
    
    categories = [choice[0] for choice in Blog.CATEGORIES]
    return render(request, 'blogs.html', {'blogs': blogs, 'categories': categories, 'selected_category': category, 'comment_form': CommentForm()})

def blog_detail_view(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    comments = blog.comments.all().order_by('created_at')
    return render(request, 'blog_detail.html', {'blog': blog, 'comments': comments, 'comment_form': CommentForm()})

def share_blog(request, blog_id):
    # Placeholder for sharing logic (e.g., increment share count, social media share)
    get_object_or_404(Blog, id=blog_id)
    return redirect('blogs')

def like_blog(request, blog_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to like posts.")
        return redirect('login')

    blog = get_object_or_404(Blog, id=blog_id)
    if blog.liked_by.filter(id=request.user.id).exists():
        blog.liked_by.remove(request.user)
        messages.info(request, f"You unliked '{blog.title}'.")
    else:
        blog.liked_by.add(request.user)
        messages.success(request, f"You liked '{blog.title}'!")
    return redirect('blogs')

@login_required
def comment_blog(request, blog_id):
    if request.method == 'POST':
        blog = get_object_or_404(Blog, id=blog_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog = blog
            comment.user = request.user
            comment.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'username': comment.user.username,
                    'text': comment.text,
                    'created_at': comment.created_at.strftime('%b %d, %I:%M %p'),
                    'count': blog.comments.count()
                })
    return redirect('blogs')

@login_required
def mentors_view(request):
    mentors = Mentor.objects.all().order_by('order')
    return render(request, 'mentors.html', {'mentors': mentors})

@login_required
def resources_view(request):
    resources = Resource.objects.all().order_by('title')
    return render(request, 'resources.html', {'resources': resources})

@login_required
def resource_suggest(request):
    if request.method == 'POST':
        form = ResourceSuggestionForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            
            return redirect('resources')
    else:
        form = ResourceSuggestionForm()
    return render(request, 'resource_suggest.html', {'form': form}) # This template will be for submitting, not displaying

def leadership_view(request):
    leaders = Leader.objects.all()
    return render(request, 'leadership.html', {'leaders': leaders})

def about_view(request):
    content = AboutContent.objects.first()
    # About page now correctly pulls fellowship Excos (Leaders)
    leaders = Leader.objects.filter(is_current=True).order_by('order')
    
    # Group past leaders by tenure
    past_leaders_raw = Leader.objects.filter(is_current=False).order_by('-tenure', 'order')
    grouped_past_leaders = {}
    for leader in past_leaders_raw:
        if leader.tenure not in grouped_past_leaders:
            grouped_past_leaders[leader.tenure] = []
        grouped_past_leaders[leader.tenure].append(leader)

    return render(request, 'about.html', {
        'content': content, 
        'leaders': leaders,
        'grouped_past_leaders': grouped_past_leaders
    })

def contact_view(request):
    if request.method == 'POST':
        ContactMessage.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            subject=request.POST.get('subject'),
            message=request.POST.get('message')
        )
        messages.success(request, "Your message has been sent successfully!")
        return redirect('contact')
    return render(request, 'contact.html')

@login_required
def prayer_request_view(request):
    if request.method == 'POST':
        name = "Anonymous" if request.POST.get('anonymous') == 'on' else request.POST.get('name', 'Anonymous')
        PrayerRequest.objects.create(
            name=name,
            email=request.POST.get('email'),
            category=request.POST.get('category', 'Prayer'),
            request=request.POST.get('request'),
            is_private=request.POST.get('is_private') == 'on'
        )
        messages.success(request, "We have received your prayer request.")
        return redirect('prayer_requests')

    # Fetch recent public prayer requests to display on the wall
    items = PrayerRequest.objects.filter(is_private=False).order_by('-created_at')[:10]
    return render(request, 'prayer_request.html', {'items': items})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('profile')
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Registration successful! Welcome to the fellowship.")
            return redirect('profile')
        messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    user = request.user
    stats = {
        'my_prayers': PrayerRequest.objects.filter(email=user.email).count(),
        'pending_requests': PrayerRequest.objects.filter(status='pending').count(),
        'prayed_requests': PrayerRequest.objects.filter(status='prayed').count(),
    }
    return render(request, 'dashboard.html', {'stats': stats})

@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        if 'image' in request.FILES:
            profile.image = request.FILES['image']
        profile.department = request.POST.get('department', profile.department)
        profile.phone_number = request.POST.get('phone_number', profile.phone_number)
        profile.bio = request.POST.get('bio', '')
        profile.skills = request.POST.get('skills', '')
        profile.website = request.POST.get('website', '')
        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')
        
    return render(request, 'profile.html', {'profile': profile})

def pray(request, item_id):
    prayer = get_object_or_404(PrayerRequest, id=item_id)
    prayer.pray_count += 1
    prayer.save()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'count': prayer.pray_count})
    return redirect('prayer_requests')