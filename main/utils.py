import calendar
from .models import Shift, Notification, TimeOff
from datetime import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils import timezone
from datetime import date, timedelta
import logging
from functools import wraps
from main import admin_roles

User = get_user_model()
logger = logging.getLogger('main')

class shiftHTMLCalendar(calendar.HTMLCalendar):
    def __init__(self, firstweekday=6, notes=None):
        super().__init__(firstweekday)
        # notes is a dictionary {day_number: "note"}
        self.notes = notes or {}

    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="noday">&nbsp;</td>'
        note = self.notes.get(day, "")
        return f'<td class="{self.cssclasses[weekday]}">{day}<br><small>{note}</small></td>'
    
def make_notification(text, user):
    notif = Notification(
        date = datetime.now(),
        notif_text = text,
        employee = user,
    )

    return notif

def generate_7day_schedule(user, day=None):
    if not day:
        day = date.today()

    shifts = Shift.objects.filter(
        employee=user,
        date__gte=datetime.now().date()
    )

    one_week_from_day = day + timedelta(days=7)
    shifts = [s for s in shifts if day <= s.date <= one_week_from_day]

    context = {}
    for i in range(7):
        current_day = day + timedelta(days=i)
        day_shifts = [s for s in shifts if s.date == current_day]
        context[f"day{i+1}"] = {
            "date": current_day,
            "shift": day_shifts[0] if day_shifts else None
        }

    return context

def manage_requests(requests, user):
    for key, value in requests.items():
        request_id = int(key.split("-")[1])
        
        if value == "a":
            logger.info("APPROVE")
            timeoff_request = TimeOff.objects.get(
                id=request_id
            )

            timeoff_request.approved = True
            timeoff_request.pending = False
            notif = make_notification(f"Your request for time off ({timeoff_request.type}) from {timeoff_request.start_time.strftime("%Y-%m-%d %H:%M")} to {timeoff_request.end_time.strftime("%Y-%m-%d %H:%M")} was approved.", user)
            notif.save()
            timeoff_request.save()

        else:
            timeoff_request = TimeOff.objects.get(
                id=request_id
            )

            timeoff_request.approved = False
            timeoff_request.pending = False
            notif = make_notification(f"Your request for time off ({timeoff_request.type}) from {timeoff_request.start_time.strftime("%Y-%m-%d %H:%M")} to {timeoff_request.end_time.strftime("%Y-%m-%d %H:%M")} was denied.", user)
            notif.save()
            timeoff_request.save()

def get_calendar_context(user, year=None, month=None):
    now = datetime.now()
    year = year or now.year
    month = month or now.month

    shifts = Shift.objects.filter(
        employee_id=user.id,
        date__year=year,
        date__month=month
    )

    time_offs = TimeOff.objects.filter(
        employee_id=user.id, 
        start_time__year=year,
        start_time__month=month
    )   

    notes = {}
    for s in shifts:
        start = s.start_time.strftime('%H:%M')
        end = s.end_time.strftime('%H:%M')
        notes[s.date.day] = f"{start} to {end}\n{s.role}"

    for t in time_offs:
        num_days = (t.end_time.date() - t.start_time.date()).days

        for i in range(num_days + 1):
            current_day = t.start_time.date() + timedelta(days=i)
            notes[current_day.day] = f"Time Off {t.type}"

    cal = shiftHTMLCalendar(notes=notes)
    shift_calendar = cal.formatmonth(year, month)

    prev_month = month - 1 or 12
    prev_year = year - 1 if month == 1 else year
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year

    today = date.today()
    one_week_from_now = today + timedelta(days=7)

    shifts = [
        s for s in shifts
        if today <= s.date <= one_week_from_now
    ]

    return {
        "shifts": shifts,
        "calendar": shift_calendar,
        "month": month,
        "year": year,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
    }

def trim_user_info(users):
    trimmed_users = {}

    for user in users:
        trimmed_users[user["id"]] = {
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "id": user["id"],
        }

    return list(trimmed_users.values())

def parse_iso_string(iso_string):
    # take iso string from html date time input and make it timezone aware with django

    try:
        fixed_string = datetime.fromisoformat(iso_string)
        fixed_string = timezone.make_aware(fixed_string, timezone.get_current_timezone())
    except:
        return False
    
    

    return fixed_string


def manager_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        user = request.user

        if getattr(user, "account_type", None) in admin_roles:
            return view_func(request, *args, **kwargs)
        return redirect("main:home")
    
    return wrapper
