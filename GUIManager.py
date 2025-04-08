import tkinter as tk
from tkinter import ttk
import sqlite3

# הגדרת מסד הנתונים
conn = sqlite3.connect("appointments.sqlite")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL
    )
""")
conn.commit()

class AppointmentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("מנהל פגישות רפואיות")
        self.geometry("400x300")

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {}

        for F in (MainMenu, AddAppointmentScreen, AppointmentListScreen, SearchByDateScreen):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainMenu)

    def show_frame(self, screen):
        frame = self.frames[screen]
        if hasattr(frame, 'refresh'):
            frame.refresh()
        frame.tkraise()


class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        label = ttk.Label(self, text="ברוך הבא למערכת ניהול פגישות", font=("Arial", 14))
        label.pack(pady=20)

        add_button = ttk.Button(self, text="הוסף פגישה חדשה", command=lambda: controller.show_frame(AddAppointmentScreen))
        add_button.pack(pady=10)

        view_button = ttk.Button(self, text="הצג את כל הפגישות", command=lambda: controller.show_frame(AppointmentListScreen))
        view_button.pack(pady=10)

        search_button = ttk.Button(self, text="חפש לפי תאריך", command=lambda: controller.show_frame(SearchByDateScreen))
        search_button.pack(pady=10)


class AddAppointmentScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ttk.Label(self, text="טופס הוספת פגישה", font=("Arial", 14))
        label.pack(pady=10)

        self.title_entry = ttk.Entry(self)
        self.title_entry.insert(0, "כותרת")
        self.title_entry.pack(pady=5)

        self.date_entry = ttk.Entry(self)
        self.date_entry.insert(0, "תאריך (YYYY-MM-DD)")
        self.date_entry.pack(pady=5)

        self.time_entry = ttk.Entry(self)
        self.time_entry.insert(0, "שעה (HH:MM)")
        self.time_entry.pack(pady=5)

        save_button = ttk.Button(self, text="שמור פגישה", command=self.save_appointment)
        save_button.pack(pady=10)

        back_button = ttk.Button(self, text="חזור", command=lambda: controller.show_frame(MainMenu))
        back_button.pack(pady=5)

    def save_appointment(self):
        title = self.title_entry.get()
        date = self.date_entry.get()
        time = self.time_entry.get()

        cursor.execute("INSERT INTO appointments (title, date, time) VALUES (?, ?, ?)", (title, date, time))
        conn.commit()

        self.title_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)


class AppointmentListScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ttk.Label(self, text="רשימת כל הפגישות", font=("Arial", 14))
        label.pack(pady=10)

        self.text = tk.Text(self, height=10, width=40)
        self.text.pack(pady=10)

        back_button = ttk.Button(self, text="חזור", command=lambda: controller.show_frame(MainMenu))
        back_button.pack(pady=5)

    def refresh(self):
        self.text.delete("1.0", tk.END)
        cursor.execute("SELECT title, date, time FROM appointments ORDER BY date, time")
        appointments = cursor.fetchall()
        for title, date, time in appointments:
            self.text.insert(tk.END, f"{date} {time} - {title}\n")


class SearchByDateScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ttk.Label(self, text="חיפוש פגישות לפי תאריך", font=("Arial", 14))
        label.pack(pady=10)

        self.date_entry = ttk.Entry(self)
        self.date_entry.insert(0, "תאריך לחיפוש (YYYY-MM-DD)")
        self.date_entry.pack(pady=5)

        search_button = ttk.Button(self, text="חפש", command=self.search)
        search_button.pack(pady=10)

        self.results_label = tk.Label(self, text="")
        self.results_label.pack(pady=10)

        back_button = ttk.Button(self, text="חזור", command=lambda: controller.show_frame(MainMenu))
        back_button.pack(pady=5)

    def search(self):
        date = self.date_entry.get()
        cursor.execute("SELECT title, time FROM appointments WHERE date = ? ORDER BY time", (date,))
        results = cursor.fetchall()

        if results:
            text = ""
            for title, time in results:
                text += f"{time} - {title}\n"
            self.results_label.config(text=text)
        else:
            self.results_label.config(text="לא נמצאו פגישות בתאריך זה.")


if __name__ == "__main__":
    app = AppointmentApp()
    app.mainloop()
    conn.close()
