import calendar
from .models import shift
from datetime import datetime

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

def get_calendar_context(user, year=None, month=None):
    now = datetime.now()
    year = year or now.year
    month = month or now.month

    shifts = shift.objects.filter(
        employee_id=user.id,
        date__year=year,
        date__month=month
    )
    
    notes = {s.date.day: f"{s.start_time} to {s.end_time}" for s in shifts}

    cal = shiftHTMLCalendar(notes=notes)
    shift_calendar = cal.formatmonth(year, month)

    prev_month = month - 1 or 12
    prev_year = year - 1 if month == 1 else year
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year

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
        }

    return trimmed_users

