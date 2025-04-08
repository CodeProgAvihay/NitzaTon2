import sqlite3
import Appointment

class DatabaseManager:
    def __init__(self, db_file="appointments.sqlite"):
        self.conn = sqlite3.connect(db_file)
        self.create_table()

    def create_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            date TEXT,
            time TEXT,
            location TEXT,
            appt_type TEXT,
            notes TEXT,
            status TEXT,
            user TEXT
        );
        '''
        self.conn.execute(query)

    def save_appointment(self, appt):
        query = '''
        INSERT INTO appointments (title, date, time, location, appt_type, notes, status, user)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        data = (
            appt.title,
            appt.date,
            appt.time,
            appt.location,
            appt.appt_type,
            appt.notes,
            appt.status,
            appt.user
        )
        self.conn.execute(query, data)
        self.conn.commit()

    def load_appointments(self):
        query = "SELECT title, date, time, location, appt_type, notes, status, user FROM appointments"
        cursor = self.conn.execute(query)

        appointments = []
        for row in cursor.fetchall():
            appt = Appointment(
                title=row[0],
                date=row[1],
                time=row[2],
                location=row[3],
                appt_type=row[4],
                notes=row[5],
                status=row[6],
                user=row[7]
            )
            appointments.append(appt)
        return appointments