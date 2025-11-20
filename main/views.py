from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Shift, TimeOff
from .utils import *
from datetime import datetime
from main import request_types, admin_roles

def home_view(request):
    if request.user.is_authenticated and request.method == 'GET':
        return redirect('main:dashboard')
    
    return render(request, "home.html")

@login_required
def dashboard_view(request):
    if request.method == "GET":
        if not request.user.first_name or not request.user.first_name:
            return redirect("main:initialization")
        
        context = {
            "role": request.user.account_type,
            "admin_roles": admin_roles,
        }

        return render(request, "dashboard.html", context)

@login_required
def manager_view(request):
    if not request.user.account_type in admin_roles:
        return redirect('main:dashboard')
    return render(request, "manager.html")

@login_required
def initialize_view(request):
    if request.method == 'POST':
        new_first_name = request.POST.get("firstname")
        new_last_name = request.POST.get("lastname")
        user = User.objects.get(id=request.user.id)

        user.first_name = new_first_name
        user.last_name = new_last_name
        user.save()

        return redirect('main:dashboard')

    return render(request, "initialization.html")
    

@login_required
def schedule_view(request):
    year = request.GET.get("year")
    month = request.GET.get("month")

    year = int(year) if year else None
    month = int(month) if month else None

    context = get_calendar_context(request.user, year, month)
    return render(request, "schedule.html", context)

@login_required
def time_off_view(request): 
    year = request.GET.get("year")
    month = request.GET.get("month")

    year = int(year) if year else None
    month = int(month) if month else None

    context = get_calendar_context(request.user, year, month)
    context["request_types"] = request_types

    if request.method == "GET":
        return render(request, "timeoff.html", context)  
    
    elif request.method == "POST":
        start_time_post = request.POST.get("start_time")
        end_time_post = request.POST.get("end_time")
        type_post= request.POST.get("type")

        start_time_post = datetime.fromisoformat(start_time_post)
        end_time_post = datetime.fromisoformat(end_time_post)
        start_time_post = timezone.make_aware(start_time_post, timezone.get_current_timezone())
        end_time_post = timezone.make_aware(end_time_post, timezone.get_current_timezone())

        timeoff_request = TimeOff(
            request_date=datetime.now().date(),
            start_time=start_time_post,
            end_time=end_time_post,
            employee=request.user,
            type=type_post,
        )

        timeoff_request.save()
        context["success"] = True

        return render(request, "timeoff.html", context)


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
            employee_id=request.user.id,
            date__year=datetime.now().year,
            date__month=datetime.now().month
        )

        context = {
            "shifts": shifts
        }

        return render(request, "swap.html", context)
    
@login_required
def edit_shift_view(request):
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
        render(request, "settings.html", context)
    else:
        render(request, "settings.html", context)

    
    return render(request, "settings.html", context)

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

@login_required
def logout_user(request):
    logout(request)
    return redirect('main:home')

### API

@login_required
def get_users(request):
    users = list(User.objects.values())
    users = trim_user_info(users)

    return JsonResponse({"users": users})
