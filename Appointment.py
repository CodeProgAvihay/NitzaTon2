from datetime import datetime

class Appointment:
    def __init__(self, title, date, time, location, appt_type, notes="", status="upcoming", user="default"):
        self.title = title              # כותרת הפגישה
        self.date = date                # תאריך (מחרוזת) בפורמט 'YYYY-MM-DD'
        self.time = time                # שעה בפורמט 'HH:MM'
        self.location = location        # מיקום הפגישה
        self.appt_type = appt_type
        self.notes = notes
        self.status = status
        self.user = user

    def get_datetime(self):
        full = self.date + " " + self.time
        dt = datetime.strptime(full, "%Y-%m-%d %H:%M")
        return dt

    def is_upcoming(self):
        now = datetime.now()
        appt_time = self.get_datetime()
        if appt_time > now:
            return True
        else:
            return False