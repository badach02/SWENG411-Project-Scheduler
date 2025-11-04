from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_validation, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('schedule/', views.home_view, name='view_schedule'),
    path('timeoff/', views.home_view, name='request_time_off'),
    path('swapshift/', views.home_view, name='swap_shift'),
    path('settings/', views.home_view, name='account_settings'),
]

