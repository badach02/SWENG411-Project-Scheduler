from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from main.forms import login_form
from .models import shift
from datetime import datetime
import calendar

User = get_user_model()

def home_view(request):
    if request.user.is_authenticated and request.method == 'GET':
        return redirect('main:dashboard')
    
    return render(request, "home.html")

def schedule_view(request):
    if request.user.is_authenticated and request.method == 'GET':
        shifts = shift.objects.filter(cover_employee_id=request.user.id)
        cal = calendar.HTMLCalendar(calendar.SUNDAY)
        shift_calendar = cal.formatmonth(datetime.now().year, datetime.now().month)

        return render(request, "schedule.html", {"shifts": shifts, "calendar": shift_calendar})
    
    return redirect("main:home")

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return render(request, "register.html", {"error": "Passwords do not match."})

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username already taken."})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            account_type="Employee"
        )

        return redirect('main:home')

    return render(request, "register.html")


def login_validation(request):
    if request.method == 'POST':
        form = login_form(request.POST)

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('main:dashboard')
        else:
            return render(request, 'home.html', {'error': 'Invalid username or password.'})

    return render(request, "home.html")

def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('main:home')
    return render(request, "dashboard.html")

def logout_user(request):
    logout(request)
    return redirect('main:home')
