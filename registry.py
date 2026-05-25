import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime

# ─── БАЗА ДАННЫХ ────────────────────────────────────────────────────────────
DB = "polyclinic.db"

def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL, birth_date TEXT,
        diagnosis TEXT, phone TEXT, address TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL, reception_days TEXT,
        specialization TEXT, cabinet_number TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS registry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER, doctor_id INTEGER,
        registration_date TEXT, appointment_datetime TEXT,
        status TEXT DEFAULT 'active', exam_results TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id),
        FOREIGN KEY(doctor_id)  REFERENCES doctors(id))""")
    cur.execute("""CREATE TABLE IF NOT EXISTS medcards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER UNIQUE, created_date TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id))""")
    con.commit()
    if cur.execute("SELECT COUNT(*) FROM doctors").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO doctors(full_name,reception_days,specialization,cabinet_number) VALUES(?,?,?,?)",
            [("Иванов Пётр Сергеевич","Пн, Ср, Пт","Терапевт","101"),
             ("Смирнова Анна Владимировна","Вт, Чт","Кардиолог","205"),
             ("Козлов Дмитрий Александрович","Пн, Вт, Ср, Чт, Пт","Хирург","312")])
    if cur.execute("SELECT COUNT(*) FROM patients").fetchone()[0] == 0:
        today = datetime.date.today().isoformat()
        for row in [("Петрова Мария Ивановна","1985-03-12","Гипертония","+7 900 111-22-33","ул. Ленина 5"),
                    ("Сидоров Алексей Николаевич","1972-07-25","Диабет II типа","+7 900 444-55-66","пр. Мира 18")]:
            cur.execute("INSERT INTO patients(full_name,birth_date,diagnosis,phone,address) VALUES(?,?,?,?,?)", row)
            cur.execute("INSERT INTO medcards(patient_id,created_date) VALUES(?,?)", (cur.lastrowid, today))
    con.commit()
    con.close()

# ─── MD3 ЗЕЛЁНАЯ ТЕМА ────────────────────────────────────────────────────────
# Material Design 3 — Tonal Green palette
BG      = "#F6FAF7"   # Surface
PANEL   = "#FFFFFF"   # Surface Container
CARD    = "#EEF5EF"   # Surface Container Low
ACCENT  = "#2D6A4F"   # Primary (deep forest green)
ACCENT2 = "#40916C"   # Secondary (medium green)
ACCENT3 = "#52B788"   # Tertiary (bright green)
TEXT    = "#1B1C1B"   # On Surface
MUTED   = "#5A6060"   # On Surface Variant
SUCCESS = "#276221"   # Positive
DANGER  = "#BA1A1A"   # Error / Red
BORDER  = "#C8D8CA"   # Outline Variant
SEL_BG  = "#C8E6C9"  # Selected row

FH1   = ("Segoe UI", 18, "bold")
FH2   = ("Segoe UI", 12, "bold")
FBODY = ("Segoe UI", 10)
FMONO = ("Consolas",  10)

def w_entry(parent, **kw):
    return tk.Entry(parent, bg=CARD, fg=TEXT, insertbackground=ACCENT,
        relief="flat", highlightthickness=1,
        highlightbackground=BORDER, highlightcolor=ACCENT2,
        font=FBODY, **kw)

def w_btn(parent, text, cmd, color=ACCENT, fg="#FFFFFF", **kw):
    b = tk.Button(parent, text=text, command=cmd,
        bg=color, fg=fg, activebackground=ACCENT2,
        activeforeground="#FFFFFF", relief="flat",
        font=("Segoe UI", 10, "bold"),
        padx=16, pady=7, cursor="hand2", bd=0, **kw)
    return b

def w_outline_btn(parent, text, cmd, **kw):
    """MD3 outlined button"""
    b = tk.Button(parent, text=text, command=cmd,
        bg=PANEL, fg=ACCENT, activebackground=CARD,
        activeforeground=ACCENT2, relief="flat",
        font=("Segoe UI", 10), highlightthickness=1,
        highlightbackground=ACCENT2, highlightcolor=ACCENT,
        padx=12, pady=6, cursor="hand2", bd=0, **kw)
    return b

def w_section(parent, text):
    return tk.Label(parent, text=text, bg=BG, fg=ACCENT, font=FH2, anchor="w")

def w_field(parent, text, bg=PANEL):
    return tk.Label(parent, text=text, bg=bg, fg=MUTED, font=("Segoe UI", 9), anchor="w")

def make_tree(parent, columns, headings, height=12):
    sty = ttk.Style()
    sty.theme_use("clam")
    sty.configure("P.Treeview",
        background=PANEL, foreground=TEXT,
        fieldbackground=PANEL, rowheight=28, font=FBODY,
        borderwidth=0)
    sty.configure("P.Treeview.Heading",
        background=CARD, foreground=ACCENT,
        font=("Segoe UI", 9, "bold"), relief="flat",
        borderwidth=0)
    sty.map("P.Treeview",
        background=[("selected", SEL_BG)],
        foreground=[("selected", ACCENT)])
    sty.layout("P.Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

    tv = ttk.Treeview(parent, columns=columns, show="headings",
        style="P.Treeview", height=height)
    for col, head in zip(columns, headings):
        tv.heading(col, text=head)
        tv.column(col, anchor="w", width=120)

    # thin scrollbar
    sb_style = ttk.Style()
    sb_style.configure("Thin.Vertical.TScrollbar",
        troughcolor=CARD, background=BORDER,
        arrowcolor=MUTED, borderwidth=0, relief="flat")
    sb = ttk.Scrollbar(parent, orient="vertical", command=tv.yview,
        style="Thin.Vertical.TScrollbar")
    tv.configure(yscrollcommand=sb.set)
    return tv, sb

def divider(parent, bg=BG):
    return tk.Frame(parent, bg=BORDER, height=1)

# ─── ВИДЖЕТ: ВЫБОР ДАТЫ КНОПКАМИ ──────────────────────────────────────────
class DatePicker(tk.Frame):
    """Compact button-based date picker (month navigation + day grid)"""
    def __init__(self, parent, variable: tk.StringVar, **kw):
        super().__init__(parent, bg=PANEL, **kw)
        self._var = variable
        try:
            self._cur = datetime.date.fromisoformat(variable.get()[:10])
        except Exception:
            self._cur = datetime.date.today()
        self._sel = self._cur
        self._build()

    DAYS_RU = ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]
    MONTHS_RU = ["Январь","Февраль","Март","Апрель","Май","Июнь",
                 "Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"]

    def _build(self):
        # nav bar
        nav = tk.Frame(self, bg=PANEL)
        nav.pack(fill="x", pady=(0,4))
        tk.Button(nav, text="◀", bg=PANEL, fg=ACCENT, relief="flat",
                  font=("Segoe UI",10,"bold"), cursor="hand2",
                  command=self._prev_month, bd=0).pack(side="left", padx=4)
        self._month_lbl = tk.Label(nav, bg=PANEL, fg=TEXT,
                                   font=("Segoe UI",10,"bold"))
        self._month_lbl.pack(side="left", expand=True)
        tk.Button(nav, text="▶", bg=PANEL, fg=ACCENT, relief="flat",
                  font=("Segoe UI",10,"bold"), cursor="hand2",
                  command=self._next_month, bd=0).pack(side="right", padx=4)
        # day-of-week header
        hdr = tk.Frame(self, bg=PANEL)
        hdr.pack()
        for i, d in enumerate(self.DAYS_RU):
            fg = DANGER if i >= 5 else MUTED
            tk.Label(hdr, text=d, bg=PANEL, fg=fg,
                     font=("Segoe UI",8), width=3, anchor="center").grid(row=0,column=i)
        # grid frame
        self._grid = tk.Frame(self, bg=PANEL)
        self._grid.pack()
        self._render()

    def _render(self):
        for w in self._grid.winfo_children():
            w.destroy()
        self._month_lbl.config(
            text=f"{self.MONTHS_RU[self._cur.month-1]} {self._cur.year}")
        first = self._cur.replace(day=1)
        start_wd = first.weekday()  # 0=Mon
        import calendar
        days_in = calendar.monthrange(self._cur.year, self._cur.month)[1]
        today = datetime.date.today()
        col = start_wd
        row = 0
        for day in range(1, days_in+1):
            d = datetime.date(self._cur.year, self._cur.month, day)
            is_sel = (d == self._sel)
            is_today = (d == today)
            wd = d.weekday()
            if is_sel:
                bg, fg = ACCENT, "#FFFFFF"
            elif is_today:
                bg, fg = SEL_BG, ACCENT
            elif wd >= 5:
                bg, fg = PANEL, DANGER
            else:
                bg, fg = PANEL, TEXT
            btn = tk.Button(self._grid, text=str(day), bg=bg, fg=fg,
                            font=("Segoe UI",9), width=3, relief="flat",
                            cursor="hand2", bd=0,
                            activebackground=SEL_BG, activeforeground=ACCENT,
                            command=lambda d=d: self._pick(d))
            btn.grid(row=row, column=col, padx=1, pady=1)
            col += 1
            if col == 7:
                col = 0
                row += 1

    def _pick(self, d):
        self._sel = d
        # preserve time part if present
        old = self._var.get()
        if len(old) > 10:
            self._var.set(d.isoformat() + old[10:])
        else:
            self._var.set(d.isoformat())
        self._render()

    def _prev_month(self):
        if self._cur.month == 1:
            self._cur = self._cur.replace(year=self._cur.year-1, month=12, day=1)
        else:
            self._cur = self._cur.replace(month=self._cur.month-1, day=1)
        self._render()

    def _next_month(self):
        if self._cur.month == 12:
            self._cur = self._cur.replace(year=self._cur.year+1, month=1, day=1)
        else:
            self._cur = self._cur.replace(month=self._cur.month+1, day=1)
        self._render()

# ─── ВИДЖЕТ: ВЫБОР ВРЕМЕНИ КНОПКАМИ ──────────────────────────────────────
class TimePicker(tk.Frame):
    """Slot-button time picker (08:00–18:00 by 30 min)"""
    SLOTS = [f"{h:02d}:{m:02d}" for h in range(8, 19) for m in (0, 30)]

    def __init__(self, parent, variable: tk.StringVar, **kw):
        super().__init__(parent, bg=PANEL, **kw)
        self._var = variable
        # extract time part
        val = variable.get()
        self._sel = val[11:16] if len(val) >= 16 else "09:00"
        if self._sel not in self.SLOTS:
            self._sel = "09:00"
        self._btns = {}
        self._build()

    def _build(self):
        tk.Label(self, text="Время приёма:", bg=PANEL, fg=MUTED,
                 font=("Segoe UI",9)).pack(anchor="w", pady=(4,4))
        grid = tk.Frame(self, bg=PANEL)
        grid.pack()
        for i, slot in enumerate(self.SLOTS):
            is_sel = (slot == self._sel)
            bg = ACCENT if is_sel else CARD
            fg = "#FFFFFF" if is_sel else TEXT
            btn = tk.Button(grid, text=slot, bg=bg, fg=fg,
                            font=("Segoe UI",9), width=5, relief="flat",
                            cursor="hand2", bd=0,
                            activebackground=SEL_BG, activeforeground=ACCENT,
                            command=lambda s=slot: self._pick(s))
            btn.grid(row=i//6, column=i%6, padx=2, pady=2)
            self._btns[slot] = btn

    def _pick(self, slot):
        # deselect old
        if self._sel in self._btns:
            self._btns[self._sel].config(bg=CARD, fg=TEXT)
        self._sel = slot
        self._btns[slot].config(bg=ACCENT, fg="#FFFFFF")
        # update variable: keep date part
        old = self._var.get()
        date_part = old[:10] if len(old) >= 10 else datetime.date.today().isoformat()
        self._var.set(f"{date_part} {slot}")

# ─── ГЛАВНОЕ ОКНО ────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ИС «Регистратура» — Поликлиника")
        self.geometry("1200x740")
        self.configure(bg=BG)
        self.resizable(True, True)
        init_db()
        self._build()

    def _build(self):
        # Header — MD3 top app bar
        hdr = tk.Frame(self, bg=ACCENT, height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="🏥  ИС «Регистратура»",
                 bg=ACCENT, fg="#FFFFFF", font=FH1).pack(side="left", padx=24, pady=12)
        tk.Label(hdr, text="Поликлиника №1",
                 bg=ACCENT, fg="#B7DFCA", font=FBODY).pack(side="right", padx=24)

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)

        # Nav rail — MD3 navigation rail
        nav = tk.Frame(body, bg=PANEL, width=180)
        nav.pack(side="left", fill="y")
        nav.pack_propagate(False)
        divider(nav, bg=BORDER).pack(fill="x")

        self.pages = {}
        self.nav_btns = []

        nav_items = [
            ("📋", "Пациенты",  "patients"),
            ("🩺", "Запись",    "appointments"),
            ("👨‍⚕️", "Врачи",    "doctors"),
            ("📊", "Отчёты",    "reports"),
        ]
        tk.Frame(nav, bg=PANEL, height=8).pack()
        for icon, label, key in nav_items:
            frm = tk.Frame(nav, bg=PANEL, cursor="hand2")
            frm.pack(fill="x", pady=2)
            inner = tk.Frame(frm, bg=PANEL, padx=12, pady=10)
            inner.pack(fill="x")
            tk.Label(inner, text=icon, bg=PANEL, fg=ACCENT,
                     font=("Segoe UI",14)).pack(side="left")
            lbl = tk.Label(inner, text=label, bg=PANEL, fg=TEXT,
                           font=("Segoe UI",10), anchor="w")
            lbl.pack(side="left", padx=8)
            # click on whole row
            for w in (frm, inner, lbl):
                w.bind("<Button-1>", lambda e, k=key: self._show(k))
            self.nav_btns.append((key, frm, lbl))

        divider(nav, bg=BORDER).pack(fill="x", pady=8)

        main = tk.Frame(body, bg=BG)
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
        for k, frm, lbl in self.nav_btns:
            if k == key:
                frm.configure(bg=SEL_BG)
                for w in frm.winfo_children():
                    w.configure(bg=SEL_BG)
                    for ww in w.winfo_children():
                        ww.configure(bg=SEL_BG)
                lbl.configure(fg=ACCENT, font=("Segoe UI",10,"bold"))
            else:
                frm.configure(bg=PANEL)
                for w in frm.winfo_children():
                    w.configure(bg=PANEL)
                    for ww in w.winfo_children():
                        ww.configure(bg=PANEL)
                lbl.configure(fg=TEXT, font=("Segoe UI",10))

# ─── СТРАНИЦА: ПАЦИЕНТЫ ──────────────────────────────────────────────────────
class PatientsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=24, pady=16)
        w_section(top, "Картотека пациентов").pack(side="left")
        w_btn(top, "🗑  Удалить", self._delete, color=DANGER).pack(side="right")
        w_btn(top, "+  Добавить", self._add).pack(side="right", padx=8)

        sf = tk.Frame(self, bg=BG)
        sf.pack(fill="x", padx=24, pady=(0, 10))
        tk.Label(sf, text="🔍 Поиск:", bg=BG, fg=MUTED, font=FBODY).pack(side="left")
        self._q = tk.StringVar()
        self._q.trace_add("write", lambda *_: self.refresh())
        e = w_entry(sf, textvariable=self._q, width=38)
        e.pack(side="left", padx=8, ipady=4)

        tf = tk.Frame(self, bg=BG)
        tf.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        cols  = ("id","full_name","birth_date","diagnosis","phone","address")
        heads = ("ID","ФИО","Дата рожд.","Диагноз","Телефон","Адрес")
        self.tv, sb = make_tree(tf, cols, heads, height=18)
        self.tv.column("full_name", width=190)
        self.tv.column("address",   width=170)
        self.tv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def refresh(self):
        q = self._q.get().strip().lower()
        con = sqlite3.connect(DB)
        rows = con.execute(
            "SELECT id,full_name,birth_date,diagnosis,phone,address FROM patients").fetchall()
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
            con.execute("DELETE FROM patients  WHERE id=?", (pid,))
            con.execute("DELETE FROM medcards  WHERE patient_id=?", (pid,))
            con.commit(); con.close()
            self.refresh()


class PatientForm(tk.Toplevel):
    def __init__(self, caller):
        super().__init__()
        self.caller = caller
        self.title("Новый пациент")
        self.configure(bg=PANEL)
        self.geometry("440x400")
        self.resizable(False, False)
        self._vars = {}
        for label, key in [
            ("ФИО", "full_name"),
            ("Дата рождения (ГГГГ-ММ-ДД)", "birth_date"),
            ("Диагноз", "diagnosis"),
            ("Телефон", "phone"),
            ("Адрес", "address"),
        ]:
            w_field(self, label).pack(padx=20, pady=(10,2), anchor="w")
            v = tk.StringVar()
            self._vars[key] = v
            w_entry(self, textvariable=v, width=46).pack(padx=20, ipady=4)
        w_btn(self, "💾  Сохранить", self._save).pack(pady=20)

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
            (d["full_name"],d["birth_date"],d["diagnosis"],d["phone"],d["address"]))
        cur.execute("INSERT INTO medcards(patient_id,created_date) VALUES(?,?)",
                    (cur.lastrowid, today))
        con.commit(); con.close()
        self.caller.refresh()
        self.destroy()

# ─── СТРАНИЦА: ЗАПИСЬ ────────────────────────────────────────────────────────
class AppointmentsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=24, pady=16)
        w_section(top, "Запись к врачу / Управление визитами").pack(side="left")
        w_btn(top, "✏  Статус", self._change_status, color=ACCENT2).pack(side="right")
        w_btn(top, "+  Записать", self._add).pack(side="right", padx=8)

        ff = tk.Frame(self, bg=BG)
        ff.pack(fill="x", padx=24, pady=(0,8))
        tk.Label(ff, text="Фильтр:", bg=BG, fg=MUTED, font=FBODY).pack(side="left")
        self._flt = tk.StringVar(value="Все")
        sty = ttk.Style()
        sty.configure("Chip.TRadiobutton", background=BG, foreground=TEXT,
                       font=("Segoe UI",10), focuscolor=BG)
        for val in ("Все","active","cancelled","completed"):
            ttk.Radiobutton(ff, text=val, variable=self._flt, value=val,
                            style="Chip.TRadiobutton",
                            command=self.refresh).pack(side="left", padx=8)

        tf = tk.Frame(self, bg=BG)
        tf.pack(fill="both", expand=True, padx=24, pady=(0,16))
        cols  = ("id","patient","doctor","reg_date","appt","status","exam")
        heads = ("ID","Пациент","Врач","Дата рег.","Дата приёма","Статус","Результат")
        self.tv, sb = make_tree(tf, cols, heads, height=18)
        self.tv.column("patient", width=165)
        self.tv.column("doctor",  width=165)
        self.tv.column("exam",    width=190)
        self.tv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def refresh(self):
        flt = self._flt.get()
        sql = """SELECT r.id, p.full_name, d.full_name,
                        r.registration_date, r.appointment_datetime,
                        r.status, r.exam_results
                 FROM registry r
                 JOIN patients p ON p.id = r.patient_id
                 JOIN doctors  d ON d.id = r.doctor_id"""
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
        self.geometry("580x620")
        self.resizable(False, False)

        con = sqlite3.connect(DB)
        self._patients = con.execute(
            "SELECT id,full_name FROM patients ORDER BY full_name").fetchall()
        self._doctors  = con.execute(
            "SELECT id,full_name,reception_days,specialization FROM doctors ORDER BY full_name").fetchall()
        con.close()

        scroll_canvas = tk.Canvas(self, bg=PANEL, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=scroll_canvas.yview)
        scroll_canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        scroll_canvas.pack(fill="both", expand=True)
        inner = tk.Frame(scroll_canvas, bg=PANEL)
        win_id = scroll_canvas.create_window((0,0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: scroll_canvas.configure(
            scrollregion=scroll_canvas.bbox("all")))
        scroll_canvas.bind("<Configure>", lambda e: scroll_canvas.itemconfig(
            win_id, width=e.width))

        w_field(inner, "Пациент:").pack(padx=20, pady=(14,2), anchor="w")
        sty = ttk.Style()
        sty.configure("MD.TCombobox", fieldbackground=CARD, background=CARD,
                       foreground=TEXT, font=FBODY)
        self._pat_cb = ttk.Combobox(inner,
            values=[f"{p[0]} — {p[1]}" for p in self._patients],
            state="readonly", width=54, font=FBODY, style="MD.TCombobox")
        self._pat_cb.pack(padx=20)

        w_field(inner, "Врач:").pack(padx=20, pady=(10,2), anchor="w")
        self._doc_cb = ttk.Combobox(inner,
            values=[f"{d[0]} — {d[1]} ({d[3]})" for d in self._doctors],
            state="readonly", width=54, font=FBODY, style="MD.TCombobox")
        self._doc_cb.pack(padx=20)
        self._doc_cb.bind("<<ComboboxSelected>>", self._on_doc)

        self._days_lbl = tk.Label(inner, text="", bg=PANEL, fg=ACCENT2,
                                  font=("Segoe UI",9,"italic"))
        self._days_lbl.pack(padx=20, anchor="w", pady=(2,0))

        divider(inner).pack(fill="x", padx=20, pady=10)

        # DateTime
        dt_now = datetime.datetime.now()
        self._appt = tk.StringVar(value=dt_now.strftime("%Y-%m-%d %H:%M"))

        tk.Label(inner, text="Дата приёма:", bg=PANEL, fg=ACCENT,
                 font=("Segoe UI",10,"bold")).pack(padx=20, anchor="w", pady=(0,6))
        self._dp = DatePicker(inner, self._appt)
        self._dp.pack(padx=20, anchor="w")

        divider(inner).pack(fill="x", padx=20, pady=8)

        self._tp = TimePicker(inner, self._appt)
        self._tp.pack(padx=20, anchor="w")

        divider(inner).pack(fill="x", padx=20, pady=10)
        w_btn(inner, "💾  Записать", self._save).pack(pady=8, padx=20, anchor="w")

    def _on_doc(self, *_):
        idx = self._doc_cb.current()
        if idx >= 0:
            self._days_lbl.configure(text=f"📅 Приёмные дни: {self._doctors[idx][2]}")

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
             datetime.date.today().isoformat(), self._appt.get(), "active"))
        con.commit(); con.close()
        self.caller.refresh()
        self.destroy()


class ChangeStatusForm(tk.Toplevel):
    def __init__(self, caller, rid):
        super().__init__()
        self.caller = caller
        self.rid = rid
        self.title(f"Статус записи #{rid}")
        self.configure(bg=PANEL)
        self.geometry("360x290")
        self.resizable(False, False)

        w_field(self, "Новый статус:").pack(padx=20, pady=(16,4), anchor="w")
        self._status = tk.StringVar(value="active")
        status_colors = {"active": SUCCESS, "cancelled": DANGER, "completed": MUTED}
        for s in ("active","cancelled","completed"):
            tk.Radiobutton(self, text=s, variable=self._status, value=s,
                bg=PANEL, fg=status_colors[s], selectcolor=SEL_BG,
                activebackground=PANEL, font=("Segoe UI",10),
                ).pack(padx=28, anchor="w", pady=2)

        w_field(self, "Результат обследования:").pack(padx=20, pady=(12,4), anchor="w")
        self._exam = tk.StringVar()
        w_entry(self, textvariable=self._exam, width=40).pack(padx=20, ipady=4)

        w_btn(self, "✅  Сохранить", self._save).pack(pady=16)

    def _save(self):
        con = sqlite3.connect(DB)
        con.execute("UPDATE registry SET status=?, exam_results=? WHERE id=?",
                    (self._status.get(), self._exam.get(), self.rid))
        con.commit(); con.close()
        self.caller.refresh()
        self.destroy()

# ─── СТРАНИЦА: ВРАЧИ (с редактированием) ─────────────────────────────────────
class DoctorsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=24, pady=16)
        w_section(top, "Врачи — сетка расписания").pack(side="left")
        w_btn(top, "🗑  Удалить",   self._delete,  color=DANGER).pack(side="right")
        w_btn(top, "✏  Изменить",  self._edit,    color=ACCENT2).pack(side="right", padx=6)
        w_btn(top, "+  Добавить",  self._add).pack(side="right", padx=6)

        tf = tk.Frame(self, bg=BG)
        tf.pack(fill="both", expand=True, padx=24, pady=(0,8))
        cols  = ("id","full_name","reception_days","specialization","cabinet_number")
        heads = ("ID","ФИО","Приёмные дни","Специализация","Кабинет")
        self.tv, sb = make_tree(tf, cols, heads, height=10)
        self.tv.column("full_name",      width=210)
        self.tv.column("reception_days", width=230)
        self.tv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        divider(self).pack(fill="x", padx=24, pady=4)
        tk.Label(self, text="Записи выбранного врача:",
                 bg=BG, fg=MUTED, font=("Segoe UI",9)).pack(padx=24, anchor="w", pady=(4,2))

        af = tk.Frame(self, bg=BG)
        af.pack(fill="both", expand=True, padx=24, pady=(0,16))
        self.atv, sb2 = make_tree(
            af, ("appt","patient","status"), ("Дата приёма","Пациент","Статус"), height=8)
        self.atv.column("appt",    width=170)
        self.atv.column("patient", width=210)
        self.atv.pack(side="left", fill="both", expand=True)
        sb2.pack(side="right", fill="y")

        self.tv.bind("<<TreeviewSelect>>", self._on_select)

    def refresh(self):
        con = sqlite3.connect(DB)
        rows = con.execute(
            "SELECT id,full_name,reception_days,specialization,cabinet_number FROM doctors").fetchall()
        con.close()
        self.tv.delete(*self.tv.get_children())
        for r in rows:
            self.tv.insert("", "end", values=r)

    def _on_select(self, *_):
        sel = self.tv.selection()
        if not sel: return
        did = self.tv.item(sel[0])["values"][0]
        con = sqlite3.connect(DB)
        rows = con.execute(
            """SELECT r.appointment_datetime, p.full_name, r.status
               FROM registry r JOIN patients p ON p.id = r.patient_id
               WHERE r.doctor_id=? ORDER BY r.appointment_datetime""", (did,)).fetchall()
        con.close()
        self.atv.delete(*self.atv.get_children())
        for r in rows:
            self.atv.insert("", "end", values=r)

    def _add(self):
        DoctorForm(self)

    def _edit(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showwarning("", "Выберите врача для редактирования")
            return
        vals = self.tv.item(sel[0])["values"]
        DoctorForm(self, doctor_id=vals[0], initial=vals)

    def _delete(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showwarning("", "Выберите врача")
            return
        did = self.tv.item(sel[0])["values"][0]
        if messagebox.askyesno("Удаление", f"Удалить врача ID {did}?\nВсе его записи тоже будут удалены."):
            con = sqlite3.connect(DB)
            con.execute("DELETE FROM registry WHERE doctor_id=?", (did,))
            con.execute("DELETE FROM doctors  WHERE id=?",        (did,))
            con.commit(); con.close()
            self.refresh()


class DoctorForm(tk.Toplevel):
    """Форма добавления / редактирования врача с выбором дней кнопками"""
    DAYS_ALL = ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]

    def __init__(self, caller, doctor_id=None, initial=None):
        super().__init__()
        self.caller    = caller
        self.doctor_id = doctor_id
        self.title("Редактировать врача" if doctor_id else "Новый врач")
        self.configure(bg=PANEL)
        self.geometry("440x460")
        self.resizable(False, False)

        # parse existing days
        existing_days = set()
        if initial and initial[2]:
            existing_days = {d.strip() for d in initial[2].split(",")}

        self._vars = {}
        fields = [
            ("ФИО",             "full_name",      initial[1] if initial else ""),
            ("Специализация",   "specialization", initial[3] if initial else ""),
            ("Кабинет",         "cabinet_number", initial[4] if initial else ""),
        ]
        for label, key, val in fields:
            w_field(self, label).pack(padx=20, pady=(12,2), anchor="w")
            v = tk.StringVar(value=str(val))
            self._vars[key] = v
            w_entry(self, textvariable=v, width=46).pack(padx=20, ipady=4)

        # Day-of-week toggle buttons
        w_field(self, "Приёмные дни:").pack(padx=20, pady=(14,6), anchor="w")
        days_frame = tk.Frame(self, bg=PANEL)
        days_frame.pack(padx=20, anchor="w")
        self._day_vars = {}
        self._day_btns = {}
        for day in self.DAYS_ALL:
            v = tk.BooleanVar(value=(day in existing_days))
            self._day_vars[day] = v
            btn = tk.Button(days_frame, text=day, width=4,
                            relief="flat", bd=0, cursor="hand2",
                            font=("Segoe UI",10,"bold"),
                            command=lambda d=day: self._toggle_day(d))
            btn.pack(side="left", padx=3)
            self._day_btns[day] = btn
            self._refresh_day_btn(day)

        divider(self).pack(fill="x", padx=20, pady=16)
        w_btn(self, "💾  Сохранить", self._save).pack(padx=20, anchor="w")

    def _refresh_day_btn(self, day):
        active = self._day_vars[day].get()
        btn = self._day_btns[day]
        if active:
            btn.configure(bg=ACCENT, fg="#FFFFFF")
        else:
            btn.configure(bg=CARD, fg=MUTED)

    def _toggle_day(self, day):
        self._day_vars[day].set(not self._day_vars[day].get())
        self._refresh_day_btn(day)

    def _save(self):
        d = {k: v.get().strip() for k, v in self._vars.items()}
        if not d["full_name"]:
            messagebox.showwarning("Ошибка", "Введите ФИО врача")
            return
        sel_days = ", ".join(day for day in self.DAYS_ALL if self._day_vars[day].get())
        con = sqlite3.connect(DB)
        if self.doctor_id:
            con.execute(
                "UPDATE doctors SET full_name=?,reception_days=?,specialization=?,cabinet_number=? WHERE id=?",
                (d["full_name"], sel_days, d["specialization"], d["cabinet_number"], self.doctor_id))
        else:
            con.execute(
                "INSERT INTO doctors(full_name,reception_days,specialization,cabinet_number) VALUES(?,?,?,?)",
                (d["full_name"], sel_days, d["specialization"], d["cabinet_number"]))
        con.commit(); con.close()
        self.caller.refresh()
        self.destroy()

# ─── СТРАНИЦА: ОТЧЁТНОСТЬ ────────────────────────────────────────────────────
class ReportsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=24, pady=16)
        w_section(top, "Отчётность — листы приёма").pack(side="left")
        w_btn(top, "🔄  Обновить", self.refresh).pack(side="right")

        # stat cards row
        cards_frame = tk.Frame(self, bg=BG)
        cards_frame.pack(fill="x", padx=24, pady=(0,16))
        self._stat_labels = {}
        stats = [
            ("pat",  "Пациентов",    "👤", ACCENT),
            ("doc",  "Врачей",       "🩺", ACCENT2),
            ("card", "Медкарт",      "📋", ACCENT3),
            ("act",  "Активных",     "✅", SUCCESS),
            ("comp", "Завершённых",  "📌", MUTED),
        ]
        for key, title, icon, color in stats:
            card = tk.Frame(cards_frame, bg=PANEL, padx=16, pady=12,
                            highlightthickness=1, highlightbackground=BORDER)
            card.pack(side="left", padx=6, fill="y")
            tk.Label(card, text=icon, bg=PANEL, fg=color,
                     font=("Segoe UI",18)).pack()
            n_lbl = tk.Label(card, text="—", bg=PANEL, fg=color,
                             font=("Segoe UI",16,"bold"))
            n_lbl.pack()
            tk.Label(card, text=title, bg=PANEL, fg=MUTED,
                     font=("Segoe UI",8)).pack()
            self._stat_labels[key] = n_lbl

        tf = tk.Frame(self, bg=BG)
        tf.pack(fill="both", expand=True, padx=24, pady=(0,16))
        cols  = ("doctor","spec","cabinet","total","active","completed","cancelled")
        heads = ("Врач","Специализация","Каб.","Всего","Актив.","Завер.","Отменено")
        self.tv, sb = make_tree(tf, cols, heads, height=16)
        self.tv.column("doctor", width=210)
        self.tv.column("spec",   width=150)
        self.tv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def refresh(self):
        con = sqlite3.connect(DB)
        self._stat_labels["pat"].configure(
            text=con.execute("SELECT COUNT(*) FROM patients").fetchone()[0])
        self._stat_labels["doc"].configure(
            text=con.execute("SELECT COUNT(*) FROM doctors").fetchone()[0])
        self._stat_labels["card"].configure(
            text=con.execute("SELECT COUNT(*) FROM medcards").fetchone()[0])
        self._stat_labels["act"].configure(
            text=con.execute("SELECT COUNT(*) FROM registry WHERE status='active'").fetchone()[0])
        self._stat_labels["comp"].configure(
            text=con.execute("SELECT COUNT(*) FROM registry WHERE status='completed'").fetchone()[0])
        rows = con.execute("""
            SELECT d.full_name, d.specialization, d.cabinet_number,
                   COUNT(r.id),
                   SUM(CASE WHEN r.status='active'    THEN 1 ELSE 0 END),
                   SUM(CASE WHEN r.status='completed' THEN 1 ELSE 0 END),
                   SUM(CASE WHEN r.status='cancelled' THEN 1 ELSE 0 END)
            FROM doctors d
            LEFT JOIN registry r ON r.doctor_id = d.id
            GROUP BY d.id ORDER BY d.full_name""").fetchall()
        con.close()
        self.tv.delete(*self.tv.get_children())
        for r in rows:
            self.tv.insert("", "end", values=r)

# ─── ЗАПУСК ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    App().mainloop()
