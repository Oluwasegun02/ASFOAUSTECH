from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about_view, name="about"),
    path("contact/", views.contact_view, name="contact"),
    path("leadership/", views.leadership_view, name="leadership"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("events/", views.events_view, name="events"),
    path("events/<int:event_id>/register/", views.register_event, name="register_event"),
    path("blogs/", views.blogs_view, name="blogs"),
    path("blogs/<int:blog_id>/share/", views.share_blog, name="share_blog"),
    path("blogs/<int:blog_id>/", views.blog_detail_view, name="blog_detail"),
    path("blogs/<int:blog_id>/like/", views.like_blog, name="like_blog"),
    path("blogs/<int:blog_id>/comment/", views.comment_blog, name="comment_blog"),
    path("mentors/", views.mentors_view, name="mentors"),

    path("resources/", views.resources_view, name="resources"),
    path("resources/suggest/", views.resource_suggest, name="resource_suggest"),
    path("alumni/", views.alumni_view, name="alumni"),
    path("alumni/register/", views.alumni_register, name="alumni_register"),
    path("prayer-requests/", views.prayer_request_view, name="prayer_requests"),
    path("prayer-requests/<str:item_id>/pray/", views.pray, name="pray"),

    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
]
