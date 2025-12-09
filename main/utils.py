import calendar
import datetime
from .models import Availability, Shift, Notification, TimeOff
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils import timezone
import logging
from functools import wraps
from main import admin_roles
import re

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
        day = datetime.date.today()

    shifts = Shift.objects.filter(
        employee=user,
        date__gte=datetime.datetime.now().date()
    )

    one_week_from_day = day + datetime.timedelta(days=7)
    shifts = [s for s in shifts if day <= s.date <= one_week_from_day]

    context = {}
    days_list = []

    for i in range(7):
        current_day = day + datetime.timedelta(days=i)
        day_shifts = [s for s in shifts if s.date == current_day]

        entry = {
            "date": current_day,
            "shift": day_shifts[0] if day_shifts else None
        }

        context[f"day{i+1}"] = entry
        days_list.append(entry)

    context["week"] = days_list

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

def get_week_endings():
    today = timezone.localdate()
    days_until_saturday = (5 - today.weekday()) % 7
    first_saturday = today + datetime.timedelta(days=days_until_saturday)

    return [
        (first_saturday + datetime.timedelta(weeks=i)).isoformat()
        for i in range(12)
    ]

def get_users_by_post_ids(id_list):
    return User.objects.filter(id__in=id_list)

def get_calendar_context(user, year=None, month=None):
    now = datetime.datetime.now()
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
            current_day = t.start_time.date() + datetime.timedelta(days=i)
            notes[current_day.day] = f"Time Off {t.type}"

    cal = shiftHTMLCalendar(notes=notes)
    shift_calendar = cal.formatmonth(year, month)

    prev_month = month - 1 or 12
    prev_year = year - 1 if month == 1 else year
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year

    today = datetime.date.today()
    one_week_from_now = today + datetime.timedelta(days=7)

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
    if not iso_string:
        return None

    try:
        if len(iso_string) == 16:
            iso_string = iso_string + ":00"

        dt = datetime.datetime.fromisoformat(iso_string)
        return timezone.make_aware(dt, timezone.get_current_timezone())
    except ValueError:
        return None

    
def manager_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        user = request.user

        if getattr(user, "account_type", None) in admin_roles:
            return view_func(request, *args, **kwargs)
        return redirect("main:home")
    
    return wrapper

def get_availability_context(user):
    try:
        availability = Availability.objects.get(employee=user)
    except Availability.DoesNotExist:
        availability = None

    context = {}
    
    if availability:
        week = availability.week
        for day_num, times in week.items():
            day_name = calendar.day_name[int(day_num)]
            context[day_name.lower()] = times
    else:
        for i in range(7):
            day_name = calendar.day_name[i]
            context[day_name.lower()] = {"start": "07:00", "end": "22:00"}

    return context

def get_week_dates_from_week_ending(week_ending_date):
    if isinstance(week_ending_date, str):
        week_ending_date = datetime.date.fromisoformat(week_ending_date)

    week_start = week_ending_date - datetime.timedelta(days=6)
    return [week_start + datetime.timedelta(days=i) for i in range(7)]


def parse_shift_templates_from_post(post_data):
    templates = {}

    for key, value in post_data.items():
        m = re.match(r"shift-(\d+)-([a-zA-Z_]+)", key)
        if m:
            idx = int(m.group(1))
            field = m.group(2)
            templates.setdefault(idx, {})[field] = value
            continue

        m2 = re.match(r"start_time_(\d+)", key)
        if m2:
            idx = int(m2.group(1))
            templates.setdefault(idx, {})["start_time"] = value
            continue

        m3 = re.match(r"end_time_(\d+)", key)
        if m3:
            idx = int(m3.group(1))
            templates.setdefault(idx, {})["end_time"] = value
            continue

        m4 = re.match(r"num_people_(\d+)", key)
        if m4:
            idx = int(m4.group(1))
            templates.setdefault(idx, {})["count"] = value
            continue

    result = []
    for idx in sorted(templates.keys()):
        t = templates[idx]
        try:
            count = int(t.get("count") or t.get("people") or 1)
        except ValueError:
            count = 1

        result.append({
            "name": t.get("name") or t.get("role") or f"Shift {idx}",
            "start": t.get("start") or t.get("start_time"),
            "end": t.get("end") or t.get("end_time"),
            "count": count,
        })

    return result

def _time_from_hhmm_string(s):
    if not s:
        return None
    try:
        return datetime.datetime.strptime(s, "%H:%M").time()
    except Exception:
        try:
            return datetime.datetime.fromisoformat(s).time()
        except Exception:
            return None

def is_employee_available(employee, day_date, shift_start_str, shift_end_str):
    s_time = _time_from_hhmm_string(shift_start_str)
    e_time = _time_from_hhmm_string(shift_end_str)
    if not s_time or not e_time:
        return False

    try:
        availability = Availability.objects.get(employee=employee)
        day_num = (day_date.weekday() + 1) % 7
        day_info = availability.week.get(str(day_num))
        if day_info:
            avail_start = _time_from_hhmm_string(day_info.get("start"))
            avail_end = _time_from_hhmm_string(day_info.get("end"))
            if not (avail_start and avail_end):
                return False
            if s_time < avail_start or e_time > avail_end:
                return False
    except Availability.DoesNotExist:
        # no availability -> assume full day available
        pass

    shift_start_dt = datetime.datetime.combine(day_date, s_time)
    shift_end_dt = datetime.datetime.combine(day_date, e_time)
    shift_start_dt = timezone.make_aware(shift_start_dt, timezone.get_current_timezone())
    shift_end_dt = timezone.make_aware(shift_end_dt, timezone.get_current_timezone())

    timeoffs = TimeOff.objects.filter(employee=employee, approved=True)
    for t in timeoffs:
        if t.start_time <= shift_end_dt and t.end_time >= shift_start_dt:
            return False

    existing = Shift.objects.filter(employee=employee, date=day_date)
    for s in existing:
        s_dt = datetime.datetime.combine(day_date, s.start_time)
        e_dt = datetime.datetime.combine(day_date, s.end_time)
        s_dt = timezone.make_aware(s_dt, timezone.get_current_timezone())
        e_dt = timezone.make_aware(e_dt, timezone.get_current_timezone())
        if s_dt <= shift_end_dt and e_dt >= shift_start_dt:
            return False

    return True

def create_schedule(user_qs, week_ending_date, templates, commit=True, relax=False):
    users = list(user_qs)
    week_dates = get_week_dates_from_week_ending(week_ending_date)

    assigned_counts = {u.id: 0 for u in users}
    assigned_hours = {u.id: 0.0 for u in users}

    for u in users:
        existing = Shift.objects.filter(employee=u, date__in=week_dates)
        total = 0.0
        for s in existing:
            dt_s = datetime.datetime.combine(s.date, s.start_time)
            dt_e = datetime.datetime.combine(s.date, s.end_time)
            total += (dt_e - dt_s).total_seconds() / 3600.0
        assigned_hours[u.id] = total

    plan = []
    created_objs = []

    for day in week_dates:
        for tpl in templates:
            start_key = tpl.get("start") or tpl.get("start_time")
            end_key = tpl.get("end") or tpl.get("end_time")
            for i in range(int(tpl.get("count", 1))):
                s_time = _time_from_hhmm_string(start_key) or datetime.datetime.strptime("07:00", "%H:%M").time()
                e_time = _time_from_hhmm_string(end_key) or datetime.datetime.strptime("15:00", "%H:%M").time()

                dur = (datetime.datetime.combine(day, e_time) - datetime.datetime.combine(day, s_time)).total_seconds() / 3600.0

                if relax:
                    candidates = list(users)
                else:
                    candidates = [u for u in users if is_employee_available(u, day, start_key, end_key)]

                if not commit:
                    def overlaps(a_start, a_end, b_start, b_end):
                        return not (a_end <= b_start or b_end <= a_start)

                    filtered = []
                    for u in candidates:
                        already = False
                        for p in plan:
                            if p['employee'] and p['employee'].id == u.id and p['date'] == day:
                                if overlaps(
                                    datetime.datetime.combine(day, p['start']),
                                    datetime.datetime.combine(day, p['end']),
                                    datetime.datetime.combine(day, s_time),
                                    datetime.datetime.combine(day, e_time),
                                ):
                                    already = True
                                    break
                        if not already:
                            filtered.append(u)
                    candidates = filtered

                candidates = [u for u in candidates if assigned_hours.get(u.id, 0.0) + dur <= 40.0]

                candidates.sort(key=lambda u: (assigned_counts.get(u.id, 0), assigned_hours.get(u.id, 0.0)))

                assigned = None
                if candidates:
                    assigned = candidates[0]
                    assigned_counts[assigned.id] = assigned_counts.get(assigned.id, 0) + 1
                    assigned_hours[assigned.id] = assigned_hours.get(assigned.id, 0.0) + dur

                entry = {
                    "date": day,
                    "start": s_time,
                    "end": e_time,
                    "employee": assigned,
                }

                if commit:
                    obj = Shift.objects.create(
                        date=day,
                        start_time=s_time,
                        end_time=e_time,
                        employee=assigned,
                    )
                    created_objs.append(obj)
                else:
                    plan.append(entry)

    return created_objs if commit else plan
