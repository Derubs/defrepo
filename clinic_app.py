import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta, date, time

# --- Модели данных ---
class Patient:
    def __init__(self, patient_id: int, name: str, dob: date):
        self.patient_id = patient_id
        self.name = name
        self.dob = dob

class Doctor:
    def __init__(self, doctor_id: int, name: str, specialization: str):
        self.doctor_id = doctor_id
        self.name = name
        self.specialization = specialization

class DoctorSchedule:
    def __init__(self, schedule_id: int, doctor_id: int, days_of_week: list, work_start_time: time, work_end_time: time):
        self.schedule_id = schedule_id
        self.doctor_id = doctor_id
        self.days_of_week = days_of_week
        self.work_start_time = work_start_time
        self.work_end_time = work_end_time

class Appointment:
    def __init__(self, appointment_id: int, patient_id: int, doctor_id: int, appointment_datetime: datetime):
        self.appointment_id = appointment_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.appointment_datetime = appointment_datetime

# --- Симуляция базы данных ---
patients_db = {
    1: Patient(1, "Иван Петров", date(1990, 5, 15)),
    2: Patient(2, "Мария Сидорова", date(1985, 11, 20)),
    3: Patient(3, "Алексей Иванов", date(2000, 1, 1))
}

doctors_db = {
    101: Doctor(101, "Андрей Смирнов", "Терапевт"),
    102: Doctor(102, "Елена Попова", "Кардиолог"),
    103: Doctor(103, "Сергей Кузнецов", "Невролог")
}

days_ru = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

doctor_schedule_db = {
    1: DoctorSchedule(1, 101, ["Понедельник", "Среда", "Пятница"], time(9, 0), time(17, 0)),
    2: DoctorSchedule(2, 102, ["Вторник", "Четверг"], time(10, 0), time(18, 0)),
    3: DoctorSchedule(3, 103, ["Суббота"], time(9, 0), time(13, 0))
}

appointments_db = []
next_appointment_id = 1


# --- Основное приложение ---
class ClinicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система записи на прием")

        self.patient_var = tk.StringVar()
        self.doctor_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.time_var = tk.StringVar()

        # Словарь: отображаемое время -> полный datetime-объект
        self._time_slots_map = {}

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 10))
        style.configure("TButton", font=("Helvetica", 10, "bold"))
        style.configure("TCombobox", font=("Helvetica", 10))
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        style.configure("Treeview", font=("Helvetica", 10), rowheight=25)

        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.booking_frame = ttk.LabelFrame(self.main_frame, text="Запись на прием", padding="10")
        self.booking_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.appointments_frame = ttk.LabelFrame(self.main_frame, text="Запланированные приемы", padding="10")
        self.appointments_frame.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Пациент
        ttk.Label(self.booking_frame, text="Пациент:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.patient_combobox = ttk.Combobox(self.booking_frame, textvariable=self.patient_var, state="readonly", width=40)
        self.patient_combobox.grid(row=0, column=1, pady=2, padx=5)
        self.patient_combobox['values'] = [f"{p.patient_id} - {p.name}" for p in patients_db.values()]
        self.patient_combobox.bind("<<ComboboxSelected>>", self.on_selection_change)

        # Врач
        ttk.Label(self.booking_frame, text="Врач:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.doctor_combobox = ttk.Combobox(self.booking_frame, textvariable=self.doctor_var, state="readonly", width=40)
        self.doctor_combobox.grid(row=1, column=1, pady=2, padx=5)
        self.doctor_combobox['values'] = [f"{d.doctor_id} - {d.name} ({d.specialization})" for d in doctors_db.values()]
        self.doctor_combobox.bind("<<ComboboxSelected>>", self.on_selection_change)

        # Дата
        ttk.Label(self.booking_frame, text="Дата приема:").grid(row=2, column=0, sticky=tk.W, pady=2)
        from tkcalendar import DateEntry
        self.date_entry = DateEntry(self.booking_frame, selectmode='day', textvariable=self.date_var, width=37, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=2, column=1, pady=2, padx=5)
        self.date_entry.bind("<<DateEntrySelected>>", self.on_date_select)

        # Время
        ttk.Label(self.booking_frame, text="Время приема:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.time_combobox = ttk.Combobox(self.booking_frame, textvariable=self.time_var, state="readonly", width=40)
        self.time_combobox.grid(row=3, column=1, pady=2, padx=5)
        self.time_combobox.set("Выберите врача и дату сначала")

        # Кнопка
        self.book_button = ttk.Button(self.booking_frame, text="Записаться на прием", command=self.create_appointment)
        self.book_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Таблица записей
        self.appointment_tree = ttk.Treeview(self.appointments_frame, columns=("ID", "Пациент", "Врач", "Время"), show="headings")
        self.appointment_tree.heading("ID", text="ID")
        self.appointment_tree.heading("Пациент", text="Пациент")
        self.appointment_tree.heading("Врач", text="Врач")
        self.appointment_tree.heading("Время", text="Время")
        self.appointment_tree.column("ID", width=50, anchor=tk.CENTER)
        self.appointment_tree.column("Пациент", width=200)
        self.appointment_tree.column("Врач", width=200)
        self.appointment_tree.column("Время", width=150, anchor=tk.CENTER)
        tree_scrollbar = ttk.Scrollbar(self.appointments_frame, orient="vertical", command=self.appointment_tree.yview)
        self.appointment_tree.configure(yscrollcommand=tree_scrollbar.set)
        self.appointment_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.appointments_frame.grid_columnconfigure(0, weight=1)
        self.appointments_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        today = date.today()
        self.date_entry.set_date(today)
        self.date_var.set(today.strftime('%Y-%m-%d'))
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.update_appointments_tree()

    def on_date_select(self, event=None):
        self.update_available_times()

    def on_selection_change(self, event=None):
        if self.patient_var.get() and self.doctor_var.get():
            self.update_available_times()

    def update_available_times(self):
        selected_doctor_info = self.doctor_var.get()
        selected_date_str = self.date_var.get()

        # Сброс
        self._time_slots_map = {}
        self.time_var.set("")
        self.time_combobox['values'] = []

        if not selected_doctor_info or not selected_date_str:
            self.time_combobox.set("Выберите врача и дату сначала")
            return

        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
            day_index = selected_date.weekday()
            current_day_of_week_ru = days_ru[day_index]

            try:
                selected_doctor_id = int(selected_doctor_info.split(" - ")[0])
            except (ValueError, IndexError):
                messagebox.showerror("Ошибка", "Некорректный формат выбора врача.")
                return

            schedule = None
            for sched in doctor_schedule_db.values():
                if sched.doctor_id == selected_doctor_id and current_day_of_week_ru in sched.days_of_week:
                    schedule = sched
                    break

            if not schedule:
                self.time_combobox.set(f"Врач не работает в {current_day_of_week_ru}")
                return

            slot_duration = timedelta(minutes=30)
            start_dt = datetime.combine(selected_date, schedule.work_start_time)
            end_dt = datetime.combine(selected_date, schedule.work_end_time)

            display_labels = []
            current_slot = start_dt
            while current_slot < end_dt:
                # Проверяем, не занят ли слот
                is_booked = any(
                    app.doctor_id == selected_doctor_id and app.appointment_datetime == current_slot
                    for app in appointments_db
                )
                if not is_booked:
                    label = current_slot.strftime("%H:%M")
                    # Если два слота попадают в одно отображаемое время (не должно, но на всякий случай)
                    # делаем ключ уникальным
                    self._time_slots_map[label] = current_slot
                    display_labels.append(label)

                current_slot += slot_duration

            if display_labels:
                self.time_combobox['values'] = display_labels
                self.time_combobox.set("Выберите время")
            else:
                self.time_combobox.set("Нет доступных слотов")

        except ValueError:
            messagebox.showerror("Ошибка даты", "Неверный формат даты. Используйте YYYY-MM-DD.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при обновлении времени: {e}")

    def create_appointment(self):
        global next_appointment_id
        try:
            selected_patient_info = self.patient_var.get()
            selected_doctor_info = self.doctor_var.get()
            selected_time_label = self.time_var.get()

            # Базовые проверки
            if not selected_patient_info or not selected_doctor_info:
                messagebox.showwarning("Внимание", "Пожалуйста, выберите пациента и врача.")
                return

            if selected_time_label not in self._time_slots_map:
                messagebox.showwarning("Внимание", "Пожалуйста, выберите доступное время приема.")
                return

            patient_id = int(selected_patient_info.split(" - ")[0])
            doctor_id = int(selected_doctor_info.split(" - ")[0])
            appointment_datetime = self._time_slots_map[selected_time_label]

            if patient_id not in patients_db:
                messagebox.showerror("Ошибка", f"Пациент с ID {patient_id} не найден.")
                return
            if doctor_id not in doctors_db:
                messagebox.showerror("Ошибка", f"Врач с ID {doctor_id} не найден.")
                return

            # Повторная проверка на занятость (на случай гонки)
            for app in appointments_db:
                if app.doctor_id == doctor_id and app.appointment_datetime == appointment_datetime:
                    messagebox.showwarning("Занято", f"Время {selected_time_label} уже занято. Выберите другое.")
                    self.update_available_times()
                    return

            new_appointment = Appointment(
                appointment_id=next_appointment_id,
                patient_id=patient_id,
                doctor_id=doctor_id,
                appointment_datetime=appointment_datetime
            )
            appointments_db.append(new_appointment)
            next_appointment_id += 1

            messagebox.showinfo(
                "Успех",
                f"Запись оформлена:\n"
                f"Пациент: {patients_db[patient_id].name}\n"
                f"Врач: {doctors_db[doctor_id].name}\n"
                f"Время: {appointment_datetime.strftime('%Y-%m-%d %H:%M')}"
            )

            self.update_appointments_tree()
            self.update_available_times()

        except (ValueError, IndexError):
            messagebox.showerror("Ошибка ввода", "Проверьте правильность выбора пациента, врача или времени.")
        except Exception as e:
            messagebox.showerror("Неизвестная ошибка", f"Произошла ошибка при записи: {e}")

    def update_appointments_tree(self):
        for item in self.appointment_tree.get_children():
            self.appointment_tree.delete(item)

        now = datetime.now()
        upcoming = sorted(
            [app for app in appointments_db if app.appointment_datetime >= now],
            key=lambda x: x.appointment_datetime
        )

        for app in upcoming:
            patient = patients_db.get(app.patient_id)
            doctor = doctors_db.get(app.doctor_id)
            if patient and doctor:
                self.appointment_tree.insert("", tk.END, values=(
                    app.appointment_id,
                    f"{patient.name} (ID:{patient.patient_id})",
                    f"{doctor.name} ({doctor.specialization})",
                    app.appointment_datetime.strftime('%Y-%m-%d %H:%M')
                ))

    def on_closing(self):
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            self.root.destroy()


# --- Запуск ---
if __name__ == "__main__":
    try:
        from tkcalendar import DateEntry
    except ImportError:
        print("Ошибка: модуль tkcalendar не найден.")
        print("Установите его: pip install tkcalendar")
        exit()

    root = tk.Tk()
    app = ClinicApp(root)
    root.mainloop()
