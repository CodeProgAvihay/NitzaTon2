class AppointmentManager:
    def __init__(self):
        self.appointments = []

    def add_appointment(self, appt):
        self.appointments.append(appt)

    def get_upcoming_appointments(self):
        upcoming = []
        for a in self.appointments:
            if a.is_upcoming():
                upcoming.append(a)
        return upcoming

    def get_appointments_by_date(self, date_str):
        result = []
        for a in self.appointments:
            if a.date == date_str:
                result.append(a)
        return result

    def mark_as_done(self, appt):
        appt.status = "done"