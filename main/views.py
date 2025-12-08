from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.timezone import now
from .models import Shift, TimeOff, Notification
from .utils import *
from datetime import datetime, date, timedelta
from main import request_types, admin_roles
from django.urls import reverse
from .utils import _time_from_hhmm_string

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
        
        context = {
            "role": request.user.account_type,
            "admin_roles": admin_roles,
            "notifications": notifs
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
    context = context | get_availability_context(request.user)
    
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
        elif request.GET.get("success") == "0":
            context["success"] = False
        
        return render(request, "timeoff.html", context)  
    
    elif request.method == "POST":
        start_time_post = parse_iso_string(request.POST.get("start_time"))
        end_time_post = parse_iso_string(request.POST.get("end_time"))

        if start_time_post == False or end_time_post == False or start_time_post >= end_time_post or start_time_post < now():
            return redirect("/timeoff?success=0")
        
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

@manager_required
def select_week_ending_view(request):
    week_dates = get_week_endings()

    if request.method == "GET":
        user_ids = request.GET.getlist("user_ids") or request.GET.get("user_ids")
        users_qs = None
        if user_ids:
            parsed_ids = []
            if isinstance(user_ids, str):
                for part in user_ids.split(","):
                    part = part.strip()
                    if part:
                        try:
                            parsed_ids.append(int(part))
                        except ValueError:
                            pass
            else:
                for item in user_ids:
                    for part in str(item).split(","):
                        part = part.strip()
                        if part:
                            try:
                                parsed_ids.append(int(part))
                            except ValueError:
                                pass
            user_ids = parsed_ids
            users_qs = get_users_by_post_ids(user_ids)
        return render(request, "select_week_ending.html", {"week_dates": week_dates, "users": users_qs})

    week_ending = request.POST.get("week_ending")
    custom = request.POST.get("custom_date")
    chosen = week_ending or custom

    user_ids = request.POST.getlist("user_ids") or request.POST.get("user_ids")
    if not user_ids:
        user_ids = [
            int(k.split("-")[1])
            for k in request.POST.keys()
            if k.startswith("user-")
        ]

    if isinstance(user_ids, str):
        user_ids = [int(u) for u in user_ids.split(",") if u.strip()]
    else:
        try:
            user_ids = [int(u) for u in user_ids]
        except Exception:
            user_ids = []

    if not chosen:
        return render(request, "select_week_ending.html", {
            "week_dates": week_dates,
            "error": "No week selected.",
            "users": get_users_by_post_ids(user_ids) if user_ids else None
        })

    try:
        chosen_date = date.fromisoformat(chosen)
    except Exception:
        return render(request, "select_week_ending.html", {
            "week_dates": week_dates,
            "error": "Invalid date selected.",
            "users": get_users_by_post_ids(user_ids)
        })

    if not user_ids:
        users_all = User.objects.all()
        return render(request, "makeschedule.html", {
            "users": users_all,
            "error": "No users were selected. Please select users to include in the schedule."
        })

    users_qs = get_users_by_post_ids(user_ids)
    return render(request, "shifts_to_cover.html", {
        "selected_week": chosen_date.isoformat(),
        "users": users_qs,
        "week_start": (chosen_date - timedelta(days=6)).isoformat(),
    })

@manager_required
def user_selection_view(request):
    if request.method == "GET":
        users = User.objects.all()
        return render(request, "makeschedule.html", {"users": users})

    elif request.method == "POST":
        selected_users = request.POST.getlist('user_ids') or []
        try:
            selected_users = [int(u) for u in selected_users]
        except Exception:
            selected_users = []

        if not selected_users:
            users = User.objects.all()
            return render(request, "makeschedule.html", {"users": users, "error": "No users selected."})

        user_ids_param = ",".join([str(u) for u in selected_users])
        url = reverse('main:select_week_ending_view') + f"?user_ids={user_ids_param}"
        return redirect(url)
    
@manager_required
def make_schedule_view(request):
    if request.method == "POST":
        users = [
            int(key.split("-")[1])
            for key in request.POST
            if key.startswith("user-")
        ]

        user_ids = request.POST.getlist("user_ids") or request.POST.get("user_ids")
        parsed_ids = []
        if isinstance(user_ids, str):
            items = [user_ids]
        else:
            items = list(user_ids) if user_ids else []

        for it in items:
            for part in str(it).split(","):
                part = part.strip()
                if part:
                    try:
                        parsed_ids.append(int(part))
                    except ValueError:
                        pass

        user_ids = parsed_ids

        week_ending = request.POST.get("week_ending")
        if not week_ending:
            return redirect("main:select_week_ending_view")

        templates = parse_shift_templates_from_post(request.POST)

        validated_templates = []
        bad = None
        for t in parse_shift_templates_from_post(request.POST):
            start = t.get('start') or t.get('start_time')
            end = t.get('end') or t.get('end_time')
            s_time = None
            e_time = None
            try:
                s_time = _time_from_hhmm_string(start)
                e_time = _time_from_hhmm_string(end)
            except Exception:
                pass

            if not s_time or not e_time:
                bad = f"Invalid time format for shift: start={start} end={end}"
                break

            if datetime.combine(date.min, s_time) >= datetime.combine(date.min, e_time):
                bad = f"Shift start must be before end: {start} - {end}"
                break

            t['start'] = start
            t['end'] = end
            validated_templates.append(t)

        if bad:
            users_qs = get_users_by_post_ids(user_ids)
            return render(request, 'shifts_to_cover.html', {
                'users': users_qs,
                'selected_week': week_ending,
                'error': bad,
            })

        templates = validated_templates

        users_qs = get_users_by_post_ids(user_ids)

        if request.POST.get("preview"):
            plan = create_schedule(users_qs, date.fromisoformat(week_ending), templates, commit=False, relax=False)

            simple_templates = []
            for t in templates:
                simple_templates.append({
                    "start": t.get("start") or t.get("start_time"),
                    "end": t.get("end") or t.get("end_time"),
                    "count": int(t.get("count", 1)),
                })

            return render(request, "schedule_preview.html", {
                "plan": plan,
                "templates": simple_templates,
                "user_ids": user_ids,
                "week_ending": week_ending,
                "week_start": (date.fromisoformat(week_ending) - timedelta(days=6)).isoformat(),
            })

        if request.POST.get("save"):
            relax = bool(request.POST.get("relax"))
            created = create_schedule(users_qs, date.fromisoformat(week_ending), templates, commit=True, relax=relax)
            for u in users_qs:
                try:
                    notif_text = f"New schedule posted for week ending {week_ending}. Please check your shifts."
                    n = Notification(date=timezone.now(), notif_text=notif_text, employee=u)
                    n.save()
                except Exception:
                    pass

            return redirect("main:manager")

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
