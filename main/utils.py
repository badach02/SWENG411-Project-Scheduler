import calendar

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