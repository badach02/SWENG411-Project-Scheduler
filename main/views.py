from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from main.forms import login_form
from .models import shift
from .utils import shiftHTMLCalendar, get_calendar_context
from datetime import datetime

User = get_user_model()

def home_view(request):
    if request.user.is_authenticated and request.method == 'GET':
        return redirect('main:dashboard')
    
    return render(request, "home.html")

@login_required
def schedule_view(request):
    year = request.GET.get("year")
    month = request.GET.get("month")

    year = int(year) if year else None
    month = int(month) if month else None

    context = get_calendar_context(request.user, year, month)
    return render(request, "schedule.html", context)

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

@login_required
def dashboard_view(request):
    return render(request, "dashboard.html")

@login_required
def logout_user(request):
    logout(request)
    return redirect('main:home')
