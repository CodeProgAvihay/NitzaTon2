import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime

BG_COLOR = "#2e3b2e"  # ירוק כהה – צבע רקע
FG_COLOR = "#d0e0d0"  # ירוק בהיר – צבע טקסט
BTN_COLOR = "#556b2f"  # זית – כפתורים
ENTRY_BG = "#3c4f3c"
ENTRY_FG = "#ffffff"

conn = sqlite3.connect("appointments.sqlite")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        soldier_name TEXT,
        injury_type TEXT,
        department TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
""")

conn.commit()

class AppointmentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("מנהל פגישות רפואיות לחיילים")
        self.geometry("500x400")

        self.user_id = None

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {}

        for F in (LoginScreen, RegisterScreen, MainMenu, AddAppointmentScreen, AppointmentListScreen, SearchByDateScreen):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginScreen)

    def show_frame(self, screen):
        frame = self.frames[screen]
        if hasattr(frame, 'refresh'):
            frame.refresh()
        frame.tkraise()

class LoginScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="התחברות", font=("Arial", 16)).pack(pady=10)

        self.username_entry = ttk.Entry(self)
        self.username_entry.insert(0, "שם משתמש")
        self.username_entry.pack(pady=5)

        self.password_entry = ttk.Entry(self, show='*')
        self.password_entry.insert(0, "סיסמה")
        self.password_entry.pack(pady=5)

        login_btn = ttk.Button(self, text="התחבר", command=self.login)
        login_btn.pack(pady=10)

        register_btn = ttk.Button(self, text="משתמש חדש", command=lambda: controller.show_frame(RegisterScreen))
        register_btn.pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
        result = cursor.fetchone()
        if result:
            self.controller.user_id = result[0]
            self.controller.show_frame(MainMenu)
        else:
            messagebox.showerror("שגיאה", "שם משתמש או סיסמה שגויים")

class RegisterScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="הרשמה", font=("Arial", 16)).pack(pady=10)

        self.username_entry = ttk.Entry(self)
        self.username_entry.insert(0, "שם משתמש")
        self.username_entry.pack(pady=5)

        self.password_entry = ttk.Entry(self, show='*')
        self.password_entry.insert(0, "סיסמה")
        self.password_entry.pack(pady=5)

        register_btn = ttk.Button(self, text="צור משתמש", command=self.register)
        register_btn.pack(pady=10)

        back_btn = ttk.Button(self, text="חזור", command=lambda: controller.show_frame(LoginScreen))
        back_btn.pack()

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("הצלחה", "המשתמש נוצר בהצלחה")
            self.controller.show_frame(LoginScreen)
        except sqlite3.IntegrityError:
            messagebox.showerror("שגיאה", "המשתמש כבר קיים")

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = ttk.Label(self, text="ברוך הבא למערכת", font=("Arial", 14))
        label.pack(pady=20)

        add_button = ttk.Button(self, text="הוסף פגישה", command=lambda: controller.show_frame(AddAppointmentScreen))
        add_button.pack(pady=10)

        view_button = ttk.Button(self, text="הצג את כל הפגישות", command=lambda: controller.show_frame(AppointmentListScreen))
        view_button.pack(pady=10)

        search_button = ttk.Button(self, text="חפש לפי תאריך", command=lambda: controller.show_frame(SearchByDateScreen))
        search_button.pack(pady=10)

        check_alert_button = ttk.Button(self, text="בדוק התראות לפגישה קרובה", command=self.check_appointments_alert)
        check_alert_button.pack(pady=10)

        logout_button = ttk.Button(self, text="התנתק", command=self.logout)
        logout_button.pack(pady=10)

    def check_appointments_alert(self):
        '''now = datetime.datetime.now()
        next_24h = now + datetime.timedelta(hours=24)

        cursor.execute("""
            SELECT title, date, time FROM appointments 
            WHERE user_id = ?
            ORDER BY date ASC, time ASC
        """, (self.controller.user_id,))

        appointments = cursor.fetchall()

        upcoming = []
        for title, date_str, time_str in appointments:
            try:
                full_dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
            except ValueError:
                continue

            if now <= full_dt <= next_24h:
                upcoming.append((title, full_dt))

        if not upcoming:
            messagebox.showinfo("תזכורות", "לא נמצאו פגישות קרובות ב־24 השעות הקרובות.")
            return

        alert_win = tk.Toplevel(self)
        alert_win.title("פגישות קרובות")
        alert_win.configure(bg=BG_COLOR)
        alert_win.geometry("400x400")

        tk.Label(alert_win, text="פגישות ב־24 השעות הקרובות", font=("Arial", 14), bg=BG_COLOR, fg=FG_COLOR).pack(pady=10)

        for title, full_dt in upcoming:
            diff = full_dt - now
            total_minutes = int(diff.total_seconds()) // 60
            hours, minutes = divmod(total_minutes, 60)

            if hours >= 6:
                color = "lightgreen"
            elif hours >= 2:
                color = "orange"
            else:
                color = "red"

            time_left_str = f"{hours} שעות ו־{minutes} דקות"
            label_text = f"{title} - בעוד {time_left_str}"
            tk.Label(alert_win, text=label_text, fg=color, bg=BG_COLOR, font=("Arial", 12)).pack(pady=2)

        tk.Button(alert_win, text="סגור", command=alert_win.destroy, bg=BTN_COLOR, fg=FG_COLOR).pack(pady=10)'''
        now = datetime.datetime.now()
        tomorrow = now + datetime.timedelta(days=1)
        cursor.execute("""SELECT title, date, time FROM appointments WHERE user_id = ?""", (self.controller.user_id,))

        upcoming = []
        for title, date_str, time_str in cursor.fetchall():
            appointment_dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
            if now <= appointment_dt <= tomorrow:
                delta = appointment_dt - now
                hours = delta.seconds // 3600
                minutes = (delta.seconds % 3600) // 60
                upcoming.append(f"{title} - בעוד {hours} שעות ו-{minutes} דקות")
        alert_win = tk.Toplevel(self)
        alert_win.title("פגישות קרובות")
        alert_win.configure(bg=BG_COLOR)
        alert_win.geometry("500x400")
        if not upcoming:
            label = tk.Label(alert_win, text="אין פגישות קרובות", bg=BG_COLOR, fg=FG_COLOR, font=("Arial", 14))
            label.pack(pady=20)
            return
        scrollbar = tk.Scrollbar(alert_win)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_box = tk.Text(alert_win, yscrollcommand=scrollbar.set, bg=ENTRY_BG, fg=ENTRY_FG, wrap="word", font=("Arial", 12))
        text_box.pack(padx=10, pady=10, expand=True, fill="both")
        scrollbar.config(command=text_box.yview)
        for item in upcoming:
            text_box.insert(tk.END, item + "\n\n")

    def logout(self):
        self.controller.user_id = None
        self.controller.show_frame(LoginScreen)


class AddAppointmentScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="הוספת פגישה", font=("Arial", 14)).pack(pady=10)

        self.title_entry = ttk.Entry(self)
        self.title_entry.insert(0, "כותרת")
        self.title_entry.pack(pady=5)

        self.soldier_entry = ttk.Entry(self)
        self.soldier_entry.insert(0, "שם החייל")
        self.soldier_entry.pack(pady=5)

        self.injury_entry = ttk.Entry(self)
        self.injury_entry.insert(0, "סוג פציעה")
        self.injury_entry.pack(pady=5)

        self.department_entry = ttk.Entry(self)
        self.department_entry.insert(0, "מחלקה")
        self.department_entry.pack(pady=5)

        self.date_entry = ttk.Entry(self)
        self.date_entry.insert(0, "תאריך (YYYY-MM-DD)")
        self.date_entry.pack(pady=5)

        self.time_entry = ttk.Entry(self)
        self.time_entry.insert(0, "שעה (HH:MM)")
        self.time_entry.pack(pady=5)

        ttk.Button(self, text="שמור פגישה", command=self.save_appointment).pack(pady=10)
        ttk.Button(self, text="חזור", command=lambda: controller.show_frame(MainMenu)).pack(pady=5)

    def save_appointment(self):
        user_id = self.controller.user_id
        title = self.title_entry.get()
        date = self.date_entry.get()
        time = self.time_entry.get()
        soldier = self.soldier_entry.get()
        injury = self.injury_entry.get()
        department = self.department_entry.get()

        cursor.execute("""
            INSERT INTO appointments (user_id, title, date, time, soldier_name, injury_type, department)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, title, date, time, soldier, injury, department))

        conn.commit()

        for entry in [self.title_entry, self.date_entry, self.time_entry, self.soldier_entry, self.injury_entry, self.department_entry]:
            entry.delete(0, tk.END)

class AppointmentListScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="רשימת פגישות", font=("Arial", 14)).pack(pady=10)

        self.text = tk.Text(self, height=15, width=60)
        self.text.pack(pady=10)

        ttk.Button(self, text="חזור", command=lambda: controller.show_frame(MainMenu)).pack(pady=5)

    def refresh(self):
        self.text.delete("1.0", tk.END)
        cursor.execute("""
            SELECT title, date, time, soldier_name, injury_type, department 
            FROM appointments 
            WHERE user_id = ? 
            ORDER BY date, time
        """, (self.controller.user_id,))
        appointments = cursor.fetchall()
        for a in appointments:
            self.text.insert(tk.END, f"{a[1]} {a[2]} - {a[0]} ({a[3]}, {a[4]}, {a[5]})\n")

class SearchByDateScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="חיפוש לפי תאריך", font=("Arial", 14)).pack(pady=10)

        self.date_entry = ttk.Entry(self)
        self.date_entry.insert(0, "תאריך לחיפוש (YYYY-MM-DD)")
        self.date_entry.pack(pady=5)

        ttk.Button(self, text="חפש", command=self.search).pack(pady=10)

        self.results_label = tk.Label(self, text="")
        self.results_label.pack(pady=10)

        ttk.Button(self, text="חזור", command=lambda: controller.show_frame(MainMenu)).pack(pady=5)

    def search(self):
        date = self.date_entry.get()
        cursor.execute("""
            SELECT title, time, soldier_name 
            FROM appointments 
            WHERE date = ? AND user_id = ? 
            ORDER BY time
        """, (date, self.controller.user_id))
        results = cursor.fetchall()

        if results:
            text = ""
            for title, time, soldier in results:
                text += f"{time} - {title} ({soldier})\n"
            self.results_label.config(text=text)
        else:
            self.results_label.config(text="לא נמצאו פגישות בתאריך זה.")

if __name__ == "__main__":
    app = AppointmentApp()
    app.mainloop()
    conn.close()
