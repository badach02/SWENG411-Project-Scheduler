from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('schedule/', views.schedule_view, name='view_schedule'),
    path('timeoff/', views.time_off_view, name='request_time_off'),
    path('swapshift/', views.swap_view, name='swap_shift'),
    path('editshift/', views.edit_shift_view, name='edit_shift'),
    path('settings/', views.settings_view, name='account_settings'),
    path('initialization/', views.initialize_view, name='initialization'),
    path('api/users/', views.get_users, name= "get_users"),

    # manager/
    path('manager/', views.manager_view, name='manager'),
    path('manager/requests', views.manage_requests_view, name='requests_manager'),
    path('manager/scheduler', views.scheduler_view, name='scheduler'),

    # manager/scheduler/
    path('manager/scheduler/maker', views.user_selection_view, name='schedule_maker'),
    path('manager/scheduler/make', views.make_schedule_view, name='make_schedule'),
    path('manager/scheduler/edit', views.scheduler_view, name='schedule_manager'),
    path('manager/scheduler/weekchooser', views.select_week_ending_view, name='select_week_ending_view'),
    path('manager/requests/<int:request_id>/', views.registration_decision_view, name='registration_decision'),
]
