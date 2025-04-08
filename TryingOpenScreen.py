import customtkinter as ctk
from tkinter import messagebox

# הגדרות כלליות
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class MindfulnessApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("מיינדפולנס ללוחם")
        self.geometry("400x600")
        self.resizable(False, False)

        self.frames = {}
        for F in (StartScreen, EmotionScreen, PracticeScreen, SummaryScreen):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame("StartScreen")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


class StartScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="ברוך הבא", font=("Segoe UI", 24)).pack(pady=40)
        self.name_entry = ctk.CTkEntry(self, placeholder_text="הכנס את שמך")
        self.name_entry.pack(pady=10)
        ctk.CTkButton(self, text="המשך", command=self.go_next).pack(pady=20)

    def go_next(self):
        name = self.name_entry.get()
        if name:
            self.controller.show_frame("EmotionScreen")
        else:
            messagebox.showwarning("שגיאה", "אנא הכנס שם")


class EmotionScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="איך אתה מרגיש היום?", font=("Segoe UI", 18)).pack(pady=20)
        emotions = ["רגוע", "לחוץ", "עייף", "שמח", "כועס"]
        self.selected_emotion = ctk.StringVar()

        for emotion in emotions:
            ctk.CTkRadioButton(self, text=emotion, variable=self.selected_emotion, value=emotion).pack(anchor="w", padx=80)

        ctk.CTkButton(self, text="המשך", command=self.go_next).pack(pady=30)

    def go_next(self):
        if self.selected_emotion.get():
            self.controller.show_frame("PracticeScreen")
        else:
            messagebox.showwarning("שגיאה", "בחר רגש")


class PracticeScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="בחר תרגול", font=("Segoe UI", 18)).pack(pady=30)
        ctk.CTkButton(self, text="תרגול נשימה", command=self.breathing).pack(pady=10)
        ctk.CTkButton(self, text="מוזיקה מרגיעה", command=self.music).pack(pady=10)
        ctk.CTkButton(self, text="כתיבה חופשית", command=self.journal).pack(pady=10)
        ctk.CTkButton(self, text="למסך סיכום", command=lambda: controller.show_frame("SummaryScreen")).pack(pady=30)

    def breathing(self):
        messagebox.showinfo("תרגול", "התחל לנשום עמוק למשך דקה")

    def music(self):
        messagebox.showinfo("מוזיקה", "מנגן מוזיקה מרגיעה...")

    def journal(self):
        messagebox.showinfo("כתיבה", "פתח חלון כתיבה חופשית")


class SummaryScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="סיכום יומי", font=("Segoe UI", 20)).pack(pady=40)
        ctk.CTkLabel(self, text="היום בחרת להרגיש... ולבצע תרגול. כל הכבוד!", wraplength=300).pack(pady=20)
        ctk.CTkButton(self, text="חזור להתחלה", command=lambda: controller.show_frame("StartScreen")).pack(pady=30)


if __name__ == "__main__":
    app = MindfulnessApp()
    app.mainloop()
