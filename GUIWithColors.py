import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime

# צבעים צבאיים
BG_COLOR = "#2e3b2e"  # ירוק כהה
FG_COLOR = "#d0e0d0"  # ירוק בהיר
BTN_COLOR = "#556b2f"  # זית

# הגדרת מסד הנתונים
conn = sqlite3.connect("appointments.db")
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
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")

conn.commit()

class AppointmentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("מנהל פגישות רפואיות לחיילים")
        self.geometry("500x400")
        self.configure(bg=BG_COLOR)

        self.user_id = None

        self.container = tk.Frame(self, bg=BG_COLOR)
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

class BaseScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_COLOR)

    def style_widget(self, widget):
        widget.configure(background=BG_COLOR, foreground=FG_COLOR)

class LoginScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="התחברות", font=("Arial", 16), background=BG_COLOR, foreground=FG_COLOR).pack(pady=10)

        self.username_entry = ttk.Entry(self)
        self.username_entry.insert(0, "שם משתמש")
        self.username_entry.pack(pady=5)

        self.password_entry = ttk.Entry(self, show='*')
        self.password_entry.insert(0, "סיסמה")
        self.password_entry.pack(pady=5)

        login_btn = tk.Button(self, text="התחבר", command=self.login, bg=BTN_COLOR, fg=FG_COLOR)
        login_btn.pack(pady=10)

        register_btn = tk.Button(self, text="משתמש חדש", command=lambda: controller.show_frame(RegisterScreen), bg=BTN_COLOR, fg=FG_COLOR)
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

class RegisterScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="הרשמה", font=("Arial", 16), background=BG_COLOR, foreground=FG_COLOR).pack(pady=10)

        self.username_entry = ttk.Entry(self)
        self.username_entry.insert(0, "שם משתמש")
        self.username_entry.pack(pady=5)

        self.password_entry = ttk.Entry(self, show='*')
        self.password_entry.insert(0, "סיסמה")
        self.password_entry.pack(pady=5)

        register_btn = tk.Button(self, text="צור משתמש", command=self.register, bg=BTN_COLOR, fg=FG_COLOR)
        register_btn.pack(pady=10)

        back_btn = tk.Button(self, text="חזור", command=lambda: controller.show_frame(LoginScreen), bg=BTN_COLOR, fg=FG_COLOR)
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

class MainMenu(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ttk.Label(self, text="ברוך הבא למערכת", font=("Arial", 14), background=BG_COLOR, foreground=FG_COLOR)
        label.pack(pady=20)

        add_button = tk.Button(self, text="הוסף פגישה", command=lambda: controller.show_frame(AddAppointmentScreen), bg=BTN_COLOR, fg=FG_COLOR)
        add_button.pack(pady=10)

        view_button = tk.Button(self, text="הצג את כל הפגישות", command=lambda: controller.show_frame(AppointmentListScreen), bg=BTN_COLOR, fg=FG_COLOR)
        view_button.pack(pady=10)

        search_button = tk.Button(self, text="חפש לפי תאריך", command=lambda: controller.show_frame(SearchByDateScreen), bg=BTN_COLOR, fg=FG_COLOR)
        search_button.pack(pady=10)

        check_alert_button = tk.Button(self, text="בדוק התראות לפגישה קרובה", command=self.check_appointments_alert, bg=BTN_COLOR, fg=FG_COLOR)
        check_alert_button.pack(pady=10)

    def check_appointments_alert(self):
        now = datetime.datetime.now()
        today_str = now.strftime('%Y-%m-%d')
        current_time = now.strftime('%H:%M')

        cursor.execute("""
            SELECT title, time FROM appointments 
            WHERE date = ? AND user_id = ?
        """, (today_str, self.controller.user_id))

        for title, time in cursor.fetchall():
            t = datetime.datetime.strptime(f"{today_str} {time}", "%Y-%m-%d %H:%M")
            diff = (t - now).total_seconds() / 60
            if 0 <= diff <= 60:
                messagebox.showinfo("תזכורת", f"פגישה קרובה בעוד {int(diff)} דקות: {title}")
