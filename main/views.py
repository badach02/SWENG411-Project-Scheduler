from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.timezone import now
from .models import Shift, TimeOff, Notification
from .utils import *
from datetime import datetime, date
from main import request_types, admin_roles
from django.contrib.auth import get_user_model
User = get_user_model()

def home_view(request):
    if request.user.is_authenticated and request.method == 'GET':
        return redirect('main:dashboard')
    
    return render(request, "home.html")

@login_required
def dashboard_view(request):
    if request.method == "GET":
        if not request.user.first_name or not request.user.last_name:
            return redirect("main:initialization")
        
        notifs = Notification.objects.filter(
            employee=request.user
        )
        
        total_employees = User.objects.filter(account_type="Employee").count()

        context = {
            "role": request.user.account_type,
            "admin_roles": admin_roles,
            "notifications": notifs,
            "total_employees": total_employees,
        }

        return render(request, "dashboard.html", context)

@login_required
def initialize_view(request):
    if request.method == 'POST':
        new_first_name = request.POST.get("firstname")
        new_last_name = request.POST.get("lastname")
        user = request.user

        user.first_name = new_first_name
        user.last_name = new_last_name

        if user.is_superuser:
            user.account_type = "admin"

        user.save()

        return redirect('main:dashboard')

    if request.user.first_name and request.user.last_name:
        return redirect("main:dashboard")
    
    return render(request, "initialization.html")
    
@login_required
def schedule_view(request):
    year = request.GET.get("year")
    month = request.GET.get("month")

    year = int(year) if year else None
    month = int(month) if month else None

    context = get_calendar_context(request.user, year, month)
    context = context | generate_7day_schedule(request.user)
    return render(request, "schedule.html", context)

@login_required
def time_off_view(request): 
    if request.method == "GET":
        year = request.GET.get("year")
        month = request.GET.get("month")
        year = int(year) if year else None
        month = int(month) if month else None

        requests = TimeOff.objects.filter(
            employee=request.user,
            pending=True,
        )

        context = get_calendar_context(request.user, year, month)
        context["request_types"] = request_types
        context["requests"] = requests

        if request.GET.get("success") == "1":
            context["success"] = True
        return render(request, "timeoff.html", context)  
    
    elif request.method == "POST":
        start_time_post = parse_iso_string(request.POST.get("start_time"))
        end_time_post = parse_iso_string(request.POST.get("end_time"))
        type_post= request.POST.get("type")

        timeoff_request = TimeOff(
            request_date=datetime.now().date(),
            start_time=start_time_post,
            end_time=end_time_post,
            employee=request.user,
            type=type_post,
        )

        timeoff_request.save()
        return redirect("/timeoff?success=1")

@login_required
def swap_view(request):
    if request.GET.get("shift"):
        swapshift = Shift.objects.get(
            id=request.GET.get("shift")
        )

        context = {
            "shift": swapshift
        }

        return render(request, "editshift.html", context)

    else:
        shifts = Shift.objects.filter(
            employee=request.user,
            date__gte=now().date()
        )

        context = {
            "shifts": shifts
        }

        return render(request, "swap.html", context)
    
@login_required
def edit_shift_view(request):
    # TODO
    pass

@login_required
def settings_view(request):
    context = {
        "role": request.user.account_type,
        "firstname": request.user.first_name,
        "lastname": request.user.last_name,
    }

    if request.method == 'POST':
        new_first_name = request.POST.get("firstname")
        new_last_name = request.POST.get("lastname")
        user = User.objects.get(id=request.user.id)

        user.first_name = new_first_name
        user.last_name = new_last_name
        user.save()

        context["firstname"] = new_first_name
        context["lastname"] =  new_last_name
        context["check"] = "Success"
        return render(request, "settings.html", context)
    else:
        return render(request, "settings.html", context)

@login_required
def logout_user(request):
    logout(request)
    return redirect('main:home')

@manager_required
def scheduler_view(request):
    return render(request, "scheduler.html")

@manager_required
def manage_requests_view(request):
    if request.method == "GET":
        requests = TimeOff.objects.filter(
            pending=True,
        )

        context = {
            "requests": requests
        }

        return render(request, "requests.html", context)
    
    if request.method == "POST":
        requests = {
            key: value[0]
            for key, value in request.POST.items()
            if key.startswith("decision-")
        }

        manage_requests(requests, request.user)

        return redirect("main:requests_manager")

@manager_required
def manager_view(request):
    return render(request, "manager.html")

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('main:dashboard')
        else:
            return render(request, 'home.html', {'error': 'Invalid username or password.'})

    return render(request, "home.html")

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

### API

@login_required
def get_users(request):
    users = list(User.objects.values())
    users = trim_user_info(users)

    return JsonResponse({"users": users})