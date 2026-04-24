"""
ИС «Регистратура» — Поликлиника
Стек: Python 3 · tkinter · sqlite3
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime

# ═══════════════════════════════════════════════
# БАЗА ДАННЫХ
# ═══════════════════════════════════════════════
DB = "polyclinic.db"


def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name  TEXT NOT NULL,
            birth_date TEXT,
            diagnosis  TEXT,
            phone      TEXT,
            address    TEXT
        )""")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name       TEXT NOT NULL,
            reception_days  TEXT,
            specialization  TEXT,
            cabinet_number  TEXT
        )""")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS registry (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id           INTEGER,
            doctor_id            INTEGER,
            registration_date    TEXT,
            appointment_datetime TEXT,
            status               TEXT DEFAULT 'active',
            exam_results         TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id),
            FOREIGN KEY(doctor_id)  REFERENCES doctors(id)
        )""")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS medcards (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id   INTEGER UNIQUE,
            created_date TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )""")

    con.commit()

    if cur.execute("SELECT COUNT(*) FROM doctors").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO doctors(full_name,reception_days,specialization,cabinet_number) VALUES(?,?,?,?)",
            [
                ("Иванов Пётр Сергеевич",        "Пн, Ср, Пт",          "Терапевт",  "101"),
                ("Смирнова Анна Владимировна",    "Вт, Чт",              "Кардиолог", "205"),
                ("Козлов Дмитрий Александрович",  "Пн, Вт, Ср, Чт, Пт", "Хирург",    "312"),
            ],
        )

    if cur.execute("SELECT COUNT(*) FROM patients").fetchone()[0] == 0:
        today = datetime.date.today().isoformat()
        for row in [
            ("Петрова Мария Ивановна",     "1985-03-12", "Гипертония",     "+7 900 111-22-33", "ул. Ленина 5"),
            ("Сидоров Алексей Николаевич", "1972-07-25", "Диабет II типа", "+7 900 444-55-66", "пр. Мира 18"),
        ]:
            cur.execute(
                "INSERT INTO patients(full_name,birth_date,diagnosis,phone,address) VALUES(?,?,?,?,?)", row
            )
            cur.execute(
                "INSERT INTO medcards(patient_id,created_date) VALUES(?,?)", (cur.lastrowid, today)
            )

    con.commit()
    con.close()


# ═══════════════════════════════════════════════
# ЦВЕТА / ШРИФТЫ
# ═══════════════════════════════════════════════
BG      = "#0f1117"
PANEL   = "#1a1d27"
CARD    = "#222536"
ACCENT  = "#4f8ef7"
ACCENT2 = "#7c5cfc"
TEXT    = "#e8eaf0"
MUTED   = "#7b82a0"
SUCCESS = "#34c47c"
DANGER  = "#f05a6a"
BORDER  = "#2e3149"

FH1   = ("Georgia",     20, "bold")
FH2   = ("Georgia",     14, "bold")
FBODY = ("Courier New", 10)


def w_entry(parent, **kw):
    return tk.Entry(
        parent, bg=CARD, fg=TEXT, insertbackground=TEXT,
        relief="flat", highlightthickness=1,
        highlightbackground=BORDER, highlightcolor=ACCENT,
        font=FBODY, **kw,
    )


def w_btn(parent, text, cmd, color=ACCENT, **kw):
    return tk.Button(
        parent, text=text, command=cmd,
        bg=color, fg="#fff", activebackground=ACCENT2,
        activeforeground="#fff", relief="flat",
        font=("Courier New", 10, "bold"),
        padx=14, pady=6, cursor="hand2", **kw,
    )


def w_section(parent, text):
    return tk.Label(parent, text=text, bg=PANEL, fg=ACCENT, font=FH2, anchor="w")


def w_field(parent, text):
    return tk.Label(parent, text=text, bg=PANEL, fg=MUTED, font=FBODY, anchor="w")


def make_tree(parent, columns, headings, height=12):
    sty = ttk.Style()
    sty.theme_use("clam")
    sty.configure("P.Treeview",
                  background=CARD, foreground=TEXT,
                  fieldbackground=CARD, rowheight=26, font=FBODY)
    sty.configure("P.Treeview.Heading",
                  background=PANEL, foreground=ACCENT,
                  font=("Courier New", 9, "bold"), relief="flat")
    sty.map("P.Treeview", background=[("selected", ACCENT2)])

    tv = ttk.Treeview(parent, columns=columns, show="headings",
                      style="P.Treeview", height=height)
    for col, head in zip(columns, headings):
        tv.heading(col, text=head)
        tv.column(col, anchor="w", width=120)

    sb = tk.Scrollbar(parent, orient="vertical", command=tv.yview,
                      bg=PANEL, troughcolor=BG)
    tv.configure(yscrollcommand=sb.set)
    return tv, sb


# ═══════════════════════════════════════════════
# ГЛАВНОЕ ОКНО
# ═══════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ИС «Регистратура» — Поликлиника")
        self.geometry("1180x720")
        self.configure(bg=BG)
        self.resizable(True, True)
        init_db()
        self._build()

    def _build(self):
        # Шапка
        hdr = tk.Frame(self, bg=PANEL, height=56)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🏥  ИС «Регистратура»",
                 bg=PANEL, fg=TEXT, font=FH1).pack(side="left", padx=20, pady=10)
        tk.Label(hdr, text="Поликлиника",
                 bg=PANEL, fg=MUTED, font=FBODY).pack(side="right", padx=20)

        # Боковая панель
        nav = tk.Frame(self, bg=PANEL, width=200)
        nav.pack(side="left", fill="y")
        nav.pack_propagate(False)
        tk.Label(nav, text="МЕНЮ", bg=PANEL, fg=MUTED,
                 font=("Courier New", 9, "bold")).pack(pady=(20, 8), padx=16, anchor="w")

        # Словари инициализируются ДО создания фреймов страниц
        self.pages = {}
        self.nav_btns = []

        for label, key in [
            ("📋  Пациенты",  "patients"),
            ("🩺  Запись",     "appointments"),
            ("👨‍⚕️  Врачи",     "doctors"),
            ("📊  Отчётность", "reports"),
        ]:
            b = tk.Button(
                nav, text=label, bg=PANEL, fg=TEXT,
                activebackground=CARD, activeforeground=ACCENT,
                relief="flat", anchor="w", padx=16, pady=10,
                font=FBODY, cursor="hand2",
                command=lambda k=key: self._show(k),
            )
            b.pack(fill="x")
            self.nav_btns.append((key, b))

        # Основная область — создаётся после словарей
        main = tk.Frame(self, bg=BG)
        main.pack(side="left", fill="both", expand=True)

        self.pages["patients"]     = PatientsPage(main)
        self.pages["appointments"] = AppointmentsPage(main)
        self.pages["doctors"]      = DoctorsPage(main)
        self.pages["reports"]      = ReportsPage(main)

        self._show("patients")

    def _show(self, key):
        for page in self.pages.values():
            page.pack_forget()
        self.pages[key].pack(fill="both", expand=True)
        self.pages[key].refresh()
        for k, b in self.nav_btns:
            b.configure(
                bg=CARD if k == key else PANEL,
                fg=ACCENT if k == key else TEXT,
            )


# ═══════════════════════════════════════════════
# СТРАНИЦА: ПАЦИЕНТЫ
# ═══════════════════════════════════════════════
class PatientsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=24, pady=16)
        w_section(top, "Картотека пациентов").pack(side="left")
        w_btn(top, "🗑 Удалить",  self._delete, color=DANGER).pack(side="right")
        w_btn(top, "+ Добавить", self._add).pack(side="right", padx=6)

        sf = tk.Frame(self, bg=BG)
        sf.pack(fill="x", padx=24, pady=(0, 10))
        tk.Label(sf, text="Поиск:", bg=BG, fg=MUTED, font=FBODY).pack(side="left")
        self._q = tk.StringVar()
        self._q.trace_add("write", lambda *_: self.refresh())
        w_entry(sf, textvariable=self._q, width=36).pack(side="left", padx=8)

        tf = tk.Frame(self, bg=BG)
        tf.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        cols  = ("id", "full_name", "birth_date", "diagnosis", "phone", "address")
        heads = ("ID", "ФИО", "Дата рожд.", "Диагноз", "Телефон", "Адрес")
        self.tv, sb = make_tree(tf, cols, heads, height=18)
        self.tv.column("full_name", width=180)
        self.tv.column("address",   width=160)
        self.tv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def refresh(self):
        q = self._q.get().strip().lower()
        con = sqlite3.connect(DB)
        rows = con.execute(
            "SELECT id,full_name,birth_date,diagnosis,phone,address FROM patients"
        ).fetchall()
        con.close()
        self.tv.delete(*self.tv.get_children())
        for r in rows:
            if not q or any(q in str(v).lower() for v in r):
                self.tv.insert("", "end", values=r)

    def _add(self):
        PatientForm(self)

    def _delete(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showwarning("Удаление", "Выберите пациента")
            return
        pid = self.tv.item(sel[0])["values"][0]
        if messagebox.askyesno("Удаление", f"Удалить пациента ID {pid}?"):
            con = sqlite3.connect(DB)
            con.execute("DELETE FROM patients WHERE id=?", (pid,))
            con.execute("DELETE FROM medcards  WHERE patient_id=?", (pid,))
            con.commit()
            con.close()
            self.refresh()


class PatientForm(tk.Toplevel):
    def __init__(self, caller):
        super().__init__()
        self.caller = caller
        self.title("Новый пациент")
        self.configure(bg=PANEL)
        self.geometry("440x380")
        self.resizable(False, False)

        self._vars = {}
        for label, key in [
            ("ФИО",                        "full_name"),
            ("Дата рождения (ГГГГ-ММ-ДД)", "birth_date"),
            ("Диагноз",                    "diagnosis"),
            ("Телефон",                    "phone"),
            ("Адрес",                      "address"),
        ]:
            w_field(self, label).pack(padx=20, pady=(10, 2), anchor="w")
            v = tk.StringVar()
            self._vars[key] = v
            w_entry(self, textvariable=v, width=46).pack(padx=20)

        w_btn(self, "💾 Сохранить", self._save).pack(pady=18)

    def _save(self):
        d = {k: v.get().strip() for k, v in self._vars.items()}
        if not d["full_name"]:
            messagebox.showwarning("Ошибка", "Введите ФИО")
            return
        today = datetime.date.today().isoformat()
        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO patients(full_name,birth_date,diagnosis,phone,address) VALUES(?,?,?,?,?)",
            (d["full_name"], d["birth_date"], d["diagnosis"], d["phone"], d["address"]),
        )
        cur.execute(
            "INSERT INTO medcards(patient_id,created_date) VALUES(?,?)", (cur.lastrowid, today)
        )
        con.commit()
        con.close()
        self.caller.refresh()
        self.destroy()


# ═══════════════════════════════════════════════
# СТРАНИЦА: ЗАПИСЬ К ВРАЧУ
# ═══════════════════════════════════════════════
class AppointmentsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=24, pady=16)
        w_section(top, "Запись к врачу / Управление визитами").pack(side="left")
        w_btn(top, "✏ Статус",   self._change_status, color=ACCENT2).pack(side="right")
        w_btn(top, "+ Записать", self._add).pack(side="right", padx=6)

        ff = tk.Frame(self, bg=BG)
        ff.pack(fill="x", padx=24, pady=(0, 8))
        tk.Label(ff, text="Фильтр:", bg=BG, fg=MUTED, font=FBODY).pack(side="left")
        self._flt = tk.StringVar(value="Все")
        for val in ("Все", "active", "cancelled", "completed"):
            tk.Radiobutton(
                ff, text=val, variable=self._flt, value=val,
                bg=BG, fg=TEXT, selectcolor=ACCENT,
                activebackground=BG, font=FBODY,
                command=self.refresh,
            ).pack(side="left", padx=6)

        tf = tk.Frame(self, bg=BG)
        tf.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        cols  = ("id", "patient", "doctor", "reg_date", "appt", "status", "exam")
        heads = ("ID", "Пациент", "Врач", "Дата рег.", "Дата приёма", "Статус", "Результат обсл.")
        self.tv, sb = make_tree(tf, cols, heads, height=18)
        self.tv.column("patient", width=160)
        self.tv.column("doctor",  width=160)
        self.tv.column("exam",    width=180)
        self.tv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def refresh(self):
        flt = self._flt.get()
        sql = """
            SELECT r.id, p.full_name, d.full_name,
                   r.registration_date, r.appointment_datetime,
                   r.status, r.exam_results
            FROM registry r
            JOIN patients p ON p.id = r.patient_id
            JOIN doctors  d ON d.id = r.doctor_id
        """
        if flt != "Все":
            sql += f" WHERE r.status = '{flt}'"
        sql += " ORDER BY r.appointment_datetime DESC"

        con = sqlite3.connect(DB)
        rows = con.execute(sql).fetchall()
        con.close()

        colors = {"active": SUCCESS, "cancelled": DANGER, "completed": MUTED}
        self.tv.delete(*self.tv.get_children())
        for r in rows:
            tag = r[5]
            self.tv.insert("", "end", values=r, tags=(tag,))
            self.tv.tag_configure(tag, foreground=colors.get(tag, TEXT))

    def _add(self):
        AppointmentForm(self)

    def _change_status(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showwarning("", "Выберите запись")
            return
        rid = self.tv.item(sel[0])["values"][0]
        ChangeStatusForm(self, rid)


class AppointmentForm(tk.Toplevel):
    def __init__(self, caller):
        super().__init__()
        self.caller = caller
        self.title("Новая запись")
        self.configure(bg=PANEL)
        self.geometry("460x340")
        self.resizable(False, False)

        con = sqlite3.connect(DB)
        self._patients = con.execute(
            "SELECT id, full_name FROM patients ORDER BY full_name"
        ).fetchall()
        self._doctors = con.execute(
            "SELECT id, full_name, reception_days, specialization FROM doctors ORDER BY full_name"
        ).fetchall()
        con.close()

        w_field(self, "Пациент:").pack(padx=20, pady=(14, 2), anchor="w")
        self._pat_cb = ttk.Combobox(
            self, values=[f"{p[0]} — {p[1]}" for p in self._patients],
            state="readonly", width=46, font=FBODY,
        )
        self._pat_cb.pack(padx=20)

        w_field(self, "Врач:").pack(padx=20, pady=(10, 2), anchor="w")
        self._doc_cb = ttk.Combobox(
            self, values=[f"{d[0]} — {d[1]} ({d[3]})" for d in self._doctors],
            state="readonly", width=46, font=FBODY,
        )
        self._doc_cb.pack(padx=20)
        self._doc_cb.bind("<<ComboboxSelected>>", self._on_doc)

        self._days_lbl = tk.Label(self, text="", bg=PANEL, fg=SUCCESS, font=FBODY)
        self._days_lbl.pack(padx=20, anchor="w")

        w_field(self, "Дата приёма (ГГГГ-ММ-ДД ЧЧ:ММ):").pack(padx=20, pady=(10, 2), anchor="w")
        self._appt = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        w_entry(self, textvariable=self._appt, width=46).pack(padx=20)

        w_btn(self, "💾 Записать", self._save).pack(pady=18)

    def _on_doc(self, *_):
        idx = self._doc_cb.current()
        if idx >= 0:
            self._days_lbl.configure(text=f"Приёмные дни: {self._doctors[idx][2]}")

    def _save(self):
        pi = self._pat_cb.current()
        di = self._doc_cb.current()
        if pi < 0 or di < 0:
            messagebox.showwarning("Ошибка", "Выберите пациента и врача")
            return
        con = sqlite3.connect(DB)
        con.execute(
            "INSERT INTO registry(patient_id,doctor_id,registration_date,appointment_datetime,status)"
            " VALUES(?,?,?,?,?)",
            (self._patients[pi][0], self._doctors[di][0],
             datetime.date.today().isoformat(), self._appt.get(), "active"),
        )
        con.commit()
        con.close()
        self.caller.refresh()
        self.destroy()


class ChangeStatusForm(tk.Toplevel):
    def __init__(self, caller, rid):
        super().__init__()
        self.caller = caller
        self.rid    = rid
        self.title(f"Статус записи #{rid}")
        self.configure(bg=PANEL)
        self.geometry("340x270")
        self.resizable(False, False)

        w_field(self, "Новый статус:").pack(padx=20, pady=(16, 4), anchor="w")
        self._status = tk.StringVar(value="active")
        for s in ("active", "cancelled", "completed"):
            tk.Radiobutton(
                self, text=s, variable=self._status, value=s,
                bg=PANEL, fg=TEXT, selectcolor=ACCENT,
                activebackground=PANEL, font=FBODY,
            ).pack(padx=28, anchor="w")

        w_field(self, "Результат обследования:").pack(padx=20, pady=(12, 4), anchor="w")
        self._exam = tk.StringVar()
        w_entry(self, textvariable=self._exam, width=36).pack(padx=20)

        w_btn(self, "✅ Сохранить", self._save).pack(pady=14)

    def _save(self):
        con = sqlite3.connect(DB)
        con.execute(
            "UPDATE registry SET status=?, exam_results=? WHERE id=?",
            (self._status.get(), self._exam.get(), self.rid),
        )
        con.commit()
        con.close()
        self.caller.refresh()
        self.destroy()


# ═══════════════════════════════════════════════
# СТРАНИЦА: ВРАЧИ
# ═══════════════════════════════════════════════
class DoctorsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=24, pady=16)
        w_section(top, "Врачи — сетка расписания").pack(side="left")

        tf = tk.Frame(self, bg=BG)
        tf.pack(fill="both", expand=True, padx=24, pady=(0, 8))
        cols  = ("id", "full_name", "reception_days", "specialization", "cabinet_number")
        heads = ("ID", "ФИО", "Приёмные дни", "Специализация", "Кабинет")
        self.tv, sb = make_tree(tf, cols, heads, height=10)
        self.tv.column("full_name",      width=200)
        self.tv.column("reception_days", width=220)
        self.tv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        tk.Label(self, text="Записи выбранного врача:",
                 bg=BG, fg=MUTED, font=FBODY).pack(padx=24, anchor="w")

        af = tk.Frame(self, bg=BG)
        af.pack(fill="both", expand=True, padx=24, pady=(4, 16))
        self.atv, sb2 = make_tree(
            af, ("appt", "patient", "status"), ("Дата приёма", "Пациент", "Статус"), height=8
        )
        self.atv.column("appt",    width=160)
        self.atv.column("patient", width=200)
        self.atv.pack(side="left", fill="both", expand=True)
        sb2.pack(side="right", fill="y")

        self.tv.bind("<<TreeviewSelect>>", self._on_select)

    def refresh(self):
        con = sqlite3.connect(DB)
        rows = con.execute(
            "SELECT id,full_name,reception_days,specialization,cabinet_number FROM doctors"
        ).fetchall()
        con.close()
        self.tv.delete(*self.tv.get_children())
        for r in rows:
            self.tv.insert("", "end", values=r)

    def _on_select(self, *_):
        sel = self.tv.selection()
        if not sel:
            return
        did = self.tv.item(sel[0])["values"][0]
        con = sqlite3.connect(DB)
        rows = con.execute(
            """SELECT r.appointment_datetime, p.full_name, r.status
               FROM registry r
               JOIN patients p ON p.id = r.patient_id
               WHERE r.doctor_id = ?
               ORDER BY r.appointment_datetime""",
            (did,),
        ).fetchall()
        con.close()
        self.atv.delete(*self.atv.get_children())
        for r in rows:
            self.atv.insert("", "end", values=r)


# ═══════════════════════════════════════════════
# СТРАНИЦА: ОТЧЁТНОСТЬ
# ═══════════════════════════════════════════════
class ReportsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=24, pady=16)
        w_section(top, "Отчётность — листы приёма").pack(side="left")
        w_btn(top, "🔄 Обновить", self.refresh).pack(side="right")

        sf = tk.Frame(self, bg=PANEL, padx=20, pady=14)
        sf.pack(fill="x", padx=24, pady=(0, 12))
        self._lbl_pat  = tk.Label(sf, bg=PANEL, fg=TEXT,    font=FBODY)
        self._lbl_doc  = tk.Label(sf, bg=PANEL, fg=TEXT,    font=FBODY)
        self._lbl_card = tk.Label(sf, bg=PANEL, fg=TEXT,    font=FBODY)
        self._lbl_act  = tk.Label(sf, bg=PANEL, fg=SUCCESS, font=FBODY)
        self._lbl_comp = tk.Label(sf, bg=PANEL, fg=MUTED,   font=FBODY)
        for lbl in (self._lbl_pat, self._lbl_doc, self._lbl_card,
                    self._lbl_act, self._lbl_comp):
            lbl.pack(side="left", padx=20)

        tf = tk.Frame(self, bg=BG)
        tf.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        cols  = ("doctor", "spec", "cabinet", "total", "active", "completed", "cancelled")
        heads = ("Врач", "Специализация", "Каб.", "Всего", "Актив.", "Завер.", "Отменено")
        self.tv, sb = make_tree(tf, cols, heads, height=16)
        self.tv.column("doctor", width=200)
        self.tv.column("spec",   width=140)
        self.tv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def refresh(self):
        con = sqlite3.connect(DB)
        n_pat  = con.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
        n_doc  = con.execute("SELECT COUNT(*) FROM doctors").fetchone()[0]
        n_card = con.execute("SELECT COUNT(*) FROM medcards").fetchone()[0]
        n_act  = con.execute("SELECT COUNT(*) FROM registry WHERE status='active'").fetchone()[0]
        n_comp = con.execute("SELECT COUNT(*) FROM registry WHERE status='completed'").fetchone()[0]

        self._lbl_pat.configure(text=f"Пациентов: {n_pat}")
        self._lbl_doc.configure(text=f"Врачей: {n_doc}")
        self._lbl_card.configure(text=f"Медкарт: {n_card}")
        self._lbl_act.configure(text=f"Активных: {n_act}")
        self._lbl_comp.configure(text=f"Завершённых: {n_comp}")

        rows = con.execute("""
            SELECT d.full_name,
                   d.specialization,
                   d.cabinet_number,
                   COUNT(r.id),
                   SUM(CASE WHEN r.status='active'    THEN 1 ELSE 0 END),
                   SUM(CASE WHEN r.status='completed' THEN 1 ELSE 0 END),
                   SUM(CASE WHEN r.status='cancelled' THEN 1 ELSE 0 END)
            FROM doctors d
            LEFT JOIN registry r ON r.doctor_id = d.id
            GROUP BY d.id
            ORDER BY d.full_name
        """).fetchall()
        con.close()

        self.tv.delete(*self.tv.get_children())
        for r in rows:
            self.tv.insert("", "end", values=r)


# ═══════════════════════════════════════════════
# ЗАПУСК
# ═══════════════════════════════════════════════
if __name__ == "__main__":
    App().mainloop()
