import math
import tkinter as tk
from tkinter import ttk, messagebox

BG_CANVAS = "#0B1220"


class ScrollableFrame(tk.Frame):

    def __init__(self, parent, bg):
        super().__init__(parent, bg=bg)

        self.canvas = tk.Canvas(
            self, bg=bg, highlightthickness=0, yscrollincrement=24
        )
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.window_id = self.canvas.create_window(
            (0, 0), window=self.inner, anchor="nw"
        )
        self._last = (0, 0)

        self.inner.bind("<Configure>", self._fit)
        self.canvas.bind("<Configure>", self._fit)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _fit(self, event=None):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        height = max(ch, self.inner.winfo_reqheight())
        if (cw, height) != self._last:
            self._last = (cw, height)
            self.canvas.itemconfig(self.window_id, width=cw, height=height)
            self.canvas.configure(scrollregion=(0, 0, cw, height))

    def _can_scroll(self):
        return self.inner.winfo_reqheight() > self.canvas.winfo_height()

    def _on_mousewheel(self, event):
        try:
            widget = self.winfo_containing(event.x_root, event.y_root)
            if widget is None:
                return
            path, mine = str(widget), str(self)
            if path != mine and not path.startswith(mine + "."):
                return
            if isinstance(widget, tk.Text) and widget.yview() != (0.0, 1.0):
                return
            if not self._can_scroll():
                return
            if event.num == 4:
                units = -1
            elif event.num == 5:
                units = 1
            else:
                units = -1 if event.delta > 0 else 1
            self.canvas.yview_scroll(units, "units")
        except (tk.TclError, KeyError):
            pass

    def destroy(self):
        try:
            self.canvas.unbind_all("<MouseWheel>")
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        except tk.TclError:
            pass
        super().destroy()


class FlowFrame(tk.Frame):

    def __init__(self, parent, bg, pad=3):
        super().__init__(parent, bg=bg)
        self.items = []
        self.pad = pad
        self._last_width = None
        self.bind("<Configure>", lambda e: self.reflow(e.width))

    def set_items(self, widgets):
        self.items = list(widgets)
        self.reflow(self.winfo_width(), force=True)

    def reflow(self, width=None, force=False):
        width = self.winfo_width() if width is None else width
        if width < 20:
            width = 10 ** 6
        if width == self._last_width and not force:
            return
        self._last_width = width
        for item in self.items:
            item.grid_forget()
        row = col = used = 0
        for item in self.items:
            need = item.winfo_reqwidth() + 2 * self.pad
            if col > 0 and used + need > width:
                row += 1
                col = used = 0
            item.grid(row=row, column=col, padx=self.pad,
                      pady=self.pad, sticky="w")
            used += need
            col += 1


class ModuleUI:

    def __init__(self, root, bg, alphabet, error_text,
                 validator=None, alert_text=""):
        self.root = root
        self.bg = bg
        self.panel = "#1B293B"
        self.alphabet = alphabet
        self.error_text = error_text
        self.validator = validator
        self.alert_text = alert_text
        self.running = False
        self.entry = self.info = self.display = self.canvas = None
        self.bottom = None
        self.write = self.clear_log = None
        self.on_start = self.on_restart = self.on_step = None
        self.on_clear = None
        self.btn_start = self.btn_restart = self.btn_step = None
        self.btn_clear = None

    def read_word(self):
        word = self.entry.get().strip()
        if not word or any(c not in self.alphabet for c in word):
            messagebox.showerror("Error", self.error_text)
            return None
        return word

    def begin(self, launch):
        if self.running:
            return
        word = self.read_word()
        if word is None:
            return
        if self.validator is not None and not self.validator(word):
            self.show_alert(word, launch)
            return
        launch(word)

    def show_alert(self, word, launch):
        dlg = tk.Toplevel(self.root)
        dlg.title("Aviso")
        dlg.configure(bg=self.panel, padx=22, pady=18)
        dlg.resizable(False, False)
        dlg.transient(self.root)

        tk.Label(
            dlg, text="La cadena no cumple la condicion",
            font=("Segoe UI", 11, "bold"),
            fg="#FACC15", bg=self.panel,
        ).pack(anchor="w")

        tk.Label(
            dlg,
            text=f"{self.alert_text}\n"
                 "Puedes cambiarla o continuar para comprobar que sea "
                 "rechazada.",
            font=("Segoe UI", 10), fg="#F1F5F9", bg=self.panel,
            justify="left", wraplength=340,
        ).pack(anchor="w", pady=(8, 14))

        buttons = tk.Frame(dlg, bg=self.panel)
        buttons.pack(anchor="e")

        def close():
            try:
                dlg.grab_release()
            except tk.TclError:
                pass
            dlg.destroy()

        def go():
            close()
            launch(word)

        def change():
            close()
            self.entry.focus_set()
            self.entry.select_range(0, "end")

        ttk.Button(buttons, text="Cambiar cadena",
                   command=change).pack(side="left", padx=4)
        continue_btn = ttk.Button(buttons, text="Continuar", command=go)
        continue_btn.pack(side="left", padx=4)

        dlg.protocol("WM_DELETE_WINDOW", change)
        dlg.bind("<Escape>", lambda e: change())
        dlg.bind("<Return>", lambda e: go())

        dlg.update_idletasks()
        w, h = dlg.winfo_reqwidth(), dlg.winfo_reqheight()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - w) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - h) // 3
        dlg.geometry(f"+{max(0, x)}+{max(0, y)}")

        continue_btn.focus_set()
        try:
            dlg.wait_visibility()
            dlg.grab_set()
        except tk.TclError:
            pass

    def load_example(self, word):
        if self.running:
            return
        self.entry.delete(0, "end")
        self.entry.insert(0, word)
        if self.on_start:
            self.on_start()

    def build_controls(self, step_text, on_start, on_restart, on_step,
                       on_clear):
        self.on_start, self.on_restart, self.on_step = (
            on_start, on_restart, on_step
        )
        self.on_clear = on_clear
        controls = tk.Frame(self.bottom, bg=self.bg)
        controls.pack()
        self.btn_start = ttk.Button(controls, text="Iniciar",
                                    command=on_start)
        self.btn_restart = ttk.Button(controls, text="Reiniciar",
                                      command=on_restart, state="disabled")
        self.btn_step = ttk.Button(controls, text=step_text,
                                   command=on_step, state="disabled")
        self.btn_clear = ttk.Button(controls, text="Borrar todo",
                                    command=on_clear)
        for btn in (self.btn_start, self.btn_restart, self.btn_step,
                    self.btn_clear):
            btn.pack(side="left", padx=5)

    def sync(self, state):
        if self.btn_step is None:
            return
        started = bool(state.get("word"))
        finished = bool(state.get("finished"))
        self.running = started and not finished
        self.btn_start.config(
            state="disabled" if self.running else "normal"
        )
        self.btn_restart.config(state="normal" if started else "disabled")
        self.btn_step.config(
            state="normal" if self.running else "disabled"
        )


class ChomskyLab:

    def __init__(self, root):
        self.root = root
        self.root.title("ChomskyLab - Jerarquia de Chomsky")
        self.root.minsize(640, 520)
        self.root.geometry(self._initial_geometry())

        self.bg = "#101827"
        self.panel = "#1B293B"
        self.accent = "#38BDF8"
        self.text = "#F1F5F9"

        self.root.configure(bg=self.bg)

        self.setup_styles()
        self.show_home()

    def _initial_geometry(self):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w = min(1150, max(640, sw - 80))
        h = min(820, max(520, sh - 120))
        return f"{w}x{h}+{max(0, (sw - w) // 2)}+{max(0, (sh - h) // 3)}"

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TButton", font=("Segoe UI", 10), padding=9)
        style.map("TButton", foreground=[("disabled", "#94A3B8")])
        style.configure("TEntry", padding=7)
        style.configure("TNotebook", background=self.bg, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            padding=[15, 8],
            font=("Segoe UI", 10, "bold"),
        )

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def title(self, parent, text, size=23):
        tk.Label(
            parent, text=text,
            font=("Segoe UI", size, "bold"),
            fg=self.text, bg=self.bg,
        ).pack(pady=10)

    def show_home(self):
        self.clear()

        scroll = ScrollableFrame(self.root, bg=self.bg)
        scroll.pack(fill="both", expand=True)
        container = tk.Frame(scroll.inner, bg=self.bg)
        container.pack(expand=True, fill="both", padx=35, pady=25)

        tk.Label(
            container, text="CHOMSKYLAB",
            font=("Segoe UI", 34, "bold"),
            fg=self.accent, bg=self.bg,
        ).pack(pady=(25, 5))

        tk.Label(
            container,
            text="SIMULADOR DE LA JERARQUIA DE CHOMSKY",
            font=("Segoe UI", 13), fg=self.text, bg=self.bg,
        ).pack(pady=5)

        tk.Label(
            container,
            text="Explora los cuatro modelos computacionales",
            font=("Segoe UI", 11), fg="#94A3B8", bg=self.bg,
        ).pack(pady=10)

        modules = [
            ("NIVEL 3 - AFD",
             "Reconocimiento de lenguajes regulares",
             self.module_afd),
            ("NIVEL 2 - PDA",
             "Reconocimiento mediante una pila LIFO",
             self.module_pda),
            ("NIVEL 1 - LBA",
             "Maquina con cinta linealmente acotada",
             self.module_lba),
            ("NIVEL 0 - MT",
             "Maquina de Turing y operaciones",
             self.module_tm),
        ]

        grid = tk.Frame(container, bg=self.bg)
        grid.pack(fill="x", pady=8)
        cards = []
        for name, description, command in modules:
            frame = tk.Frame(grid, bg=self.panel, padx=15, pady=10)

            tk.Label(
                frame, text=name,
                font=("Segoe UI", 13, "bold"),
                fg=self.accent, bg=self.panel,
            ).pack(anchor="w")

            tk.Label(
                frame, text=description,
                font=("Segoe UI", 10),
                fg=self.text, bg=self.panel,
            ).pack(anchor="w", pady=3)

            ttk.Button(
                frame, text="Abrir modulo", command=command
            ).pack(anchor="e", pady=3)
            cards.append(frame)

        layout = {"cols": 0}

        def reflow(event=None):
            cols = 2 if grid.winfo_width() >= 820 else 1
            if cols == layout["cols"]:
                return
            layout["cols"] = cols
            for i, card in enumerate(cards):
                card.grid(row=i // cols, column=i % cols, sticky="nsew",
                          padx=8, pady=7)
            for c in range(2):
                grid.columnconfigure(
                    c, weight=1 if c < cols else 0, uniform="card"
                )

        grid.bind("<Configure>", reflow)
        reflow()

        tk.Label(
            container,
            text="Sarah Chaves - Automatas, grámaticas y lenguajes",
            fg="#64748B", bg=self.bg, font=("Segoe UI", 9),
        ).pack(side="bottom", pady=15)

    def create_module(self, key, name, description, examples, alphabet,
                      error_text, validator=None, alert_text=""):
        self.clear()
        ui = ModuleUI(self.root, self.bg, alphabet, error_text,
                      validator, alert_text)

        header = tk.Frame(self.root, bg=self.bg)
        header.pack(fill="x", padx=20, pady=10)

        ttk.Button(
            header, text="< Volver al inicio",
            command=self.show_home,
        ).pack(side="left")

        tk.Label(
            header, text=name,
            font=("Segoe UI", 20, "bold"),
            fg=self.accent, bg=self.bg,
        ).pack(side="left", padx=25)

        desc = tk.Label(
            self.root, text=description,
            font=("Segoe UI", 10),
            fg="#94A3B8", bg=self.bg, wraplength=600,
        )
        desc.pack(fill="x", padx=20, pady=5)
        desc.bind("<Configure>",
                  lambda e: desc.config(wraplength=max(200, e.width - 20)))

        bottom = tk.Frame(self.root, bg=self.bg)
        bottom.pack(side="bottom", fill="x", pady=8)
        ui.bottom = bottom

        scroll = ScrollableFrame(self.root, bg=self.bg)
        scroll.pack(fill="both", expand=True, padx=20, pady=5)
        body = scroll.inner

        entry_frame = tk.Frame(body, bg=self.panel, padx=15, pady=12)
        entry_frame.pack(fill="x", pady=(5, 8))

        tk.Label(
            entry_frame, text="Cadena de entrada:",
            bg=self.panel, fg=self.text,
        ).pack(side="left")

        entry = ttk.Entry(entry_frame, font=("Consolas", 12))
        entry.pack(side="left", fill="x", expand=True, padx=12)
        entry.bind("<Return>",
                   lambda e: ui.on_start() if ui.on_start else None)
        ui.entry = entry

        hint = tk.Label(
            body,
            text=("Escribe tu propia cadena y pulsa Enter o Iniciar, o pulsa "
                  "un ejemplo para cargarlo e iniciar la simulacion al "
                  "instante."),
            font=("Segoe UI", 9, "italic"),
            fg="#94A3B8", bg=self.bg,
            wraplength=600, justify="left", anchor="w",
        )
        hint.pack(fill="x", pady=(0, 6))
        hint.bind("<Configure>",
                  lambda e: hint.config(wraplength=max(200, e.width - 10)))

        examples_frame = tk.Frame(body, bg=self.panel, padx=15, pady=8)
        examples_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            examples_frame, text="Ejemplos rapidos (un clic inicia):",
            bg=self.panel, fg=self.text,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")

        flow = FlowFrame(examples_frame, bg=self.panel)
        flow.pack(fill="x", pady=(4, 0))
        flow.set_items([
            ttk.Button(
                flow, text=ex, width=max(6, len(ex) + 2),
                command=lambda x=ex: ui.load_example(x),
            )
            for ex in examples
        ])

        visual = tk.Frame(body, bg=self.panel, padx=15, pady=12)
        visual.pack(fill="both", expand=True, pady=8)

        info = tk.Label(
            visual, text="Preparado para iniciar la simulacion",
            font=("Segoe UI", 12),
            fg=self.accent, bg=self.panel,
        )
        info.pack(pady=6)

        canvas = tk.Canvas(
            visual, bg=BG_CANVAS, height=300,
            highlightthickness=1, highlightbackground="#334155",
        )
        canvas.pack(fill="both", expand=True, pady=8)

        display = tk.Label(
            visual, text="",
            font=("Consolas", 11, "bold"),
            fg=self.text, bg=self.panel,
            justify="left", wraplength=800,
        )
        display.pack(fill="x", pady=6)
        visual.bind("<Configure>",
                    lambda e: display.config(wraplength=max(240, e.width - 60)))

        log_frame = tk.Frame(visual, bg=self.panel)
        log_frame.pack(fill="x", pady=6)
        log = tk.Text(
            log_frame, height=6,
            bg=BG_CANVAS, fg="#A7F3D0",
            font=("Consolas", 10),
            state="disabled", wrap="word",
        )
        log_bar = ttk.Scrollbar(log_frame, orient="vertical",
                                command=log.yview)
        log.configure(yscrollcommand=log_bar.set)
        log_bar.pack(side="right", fill="y")
        log.pack(side="left", fill="x", expand=True)

        def write_log(message):
            log.config(state="normal")
            log.insert("end", message + "\n")
            log.see("end")
            log.config(state="disabled")

        def clear_log():
            log.config(state="normal")
            log.delete("1.0", "end")
            log.config(state="disabled")

        ui.info, ui.display, ui.canvas = info, display, canvas
        ui.write, ui.clear_log = write_log, clear_log
        return ui

    @staticmethod
    def _size(canvas):
        w, h = canvas.winfo_width(), canvas.winfo_height()
        return (w if w >= 100 else 900), (h if h >= 100 else 300)

    @staticmethod
    def _scale(w, h, base_w=900, base_h=330):
        return max(0.65, min(1.25, w / base_w, h / base_h))

    @staticmethod
    def _bezier(p0, c, p1, n=28):
        pts = []
        for i in range(n + 1):
            t = i / n
            a, b, d = (1 - t) ** 2, 2 * t * (1 - t), t * t
            pts.append((a * p0[0] + b * c[0] + d * p1[0],
                        a * p0[1] + b * c[1] + d * p1[1]))
        return pts

    @staticmethod
    def _bezier3(p0, c1, c2, p1, n=32):
        pts = []
        for i in range(n + 1):
            t = i / n
            a = (1 - t) ** 3
            b = 3 * t * (1 - t) ** 2
            d = 3 * t * t * (1 - t)
            e = t ** 3
            pts.append((a * p0[0] + b * c1[0] + d * c2[0] + e * p1[0],
                        a * p0[1] + b * c1[1] + d * c2[1] + e * p1[1]))
        return pts

    @staticmethod
    def _trim(pts, ca, ra, cb, rb):
        start = 0
        while (start < len(pts) - 1 and
               math.hypot(pts[start][0] - ca[0], pts[start][1] - ca[1]) < ra + 1):
            start += 1
        end = len(pts) - 1
        while (end > start and
               math.hypot(pts[end][0] - cb[0], pts[end][1] - cb[1]) < rb + 3):
            end -= 1
        return pts[start:end + 1]

    def _label(self, canvas, x, y, text, size=10, fg="#FACC15"):
        tid = canvas.create_text(x, y, text=text,
                                 font=("Segoe UI", size, "bold"), fill=fg)
        box = canvas.bbox(tid)
        if box:
            bg = canvas.create_rectangle(box[0] - 2, box[1] - 1,
                                         box[2] + 2, box[3] + 1,
                                         fill=BG_CANVAS, outline="")
            canvas.tag_lower(bg, tid)
        return tid

    def _edge(self, canvas, a, b, ra, rb, label, bend=0, s=1.0,
              color="#94A3B8"):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy) or 1
        nx, ny = dy / length, -dx / length
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        ctrl = (mx + nx * bend, my + ny * bend)
        pts = self._trim(self._bezier(a, ctrl, b), a, ra, b, rb)
        flat = [v for p in pts for v in p]
        canvas.create_line(*flat, arrow="last", arrowshape=(10, 12, 4),
                           fill=color, width=2)
        gap = 15 * s + 2
        if bend > 0:
            off = bend / 2 + gap
        elif ny > 0:
            off = -gap
        else:
            off = gap
        self._label(canvas, mx + nx * off, my + ny * off, label,
                    size=max(8, int(10 * s)))

    def _loop(self, canvas, c, r, label, height, s=1.0, color="#94A3B8"):
        x, y = c
        a0, a1 = math.radians(-125), math.radians(-55)
        p0 = (x + r * math.cos(a0), y + r * math.sin(a0))
        p1 = (x + r * math.cos(a1), y + r * math.sin(a1))
        top = y - r - height
        pts = self._bezier3(p0, (p0[0] - 0.35 * r, top),
                            (p1[0] + 0.35 * r, top), p1)
        flat = [v for p in pts for v in p]
        canvas.create_line(*flat, arrow="last", arrowshape=(10, 12, 4),
                           fill=color, width=2)
        peak_y = y - 0.955 * r - 0.75 * height
        self._label(canvas, x, peak_y - 11 * s - 4, label,
                    size=max(8, int(9 * s)))

    def _node(self, canvas, c, r, name, active, accepting=False, s=1.0):
        x, y = c
        fill = "#38BDF8" if active else "#334155"
        canvas.create_oval(x - r, y - r, x + r, y + r,
                           fill=fill, outline="#F1F5F9", width=2)
        canvas.create_text(x, y, text=name,
                           font=("Segoe UI", max(9, int(12 * s)), "bold"),
                           fill="#F1F5F9")
        if accepting:
            canvas.create_oval(x - r - 6, y - r - 6, x + r + 6, y + r + 6,
                               outline="#F1F5F9", width=2)

    def _start_arrow(self, canvas, c, r, s, label=True):
        x, y = c
        x_end = x - r - 3
        x_start = max(6, x_end - 44 * s)
        canvas.create_line(x_start, y, x_end, y, arrow="last",
                           arrowshape=(10, 12, 4), fill="#F1F5F9", width=2)
        if label:
            canvas.create_text(x_start + 2, y - 13, text="inicio", anchor="w",
                               font=("Segoe UI", max(8, int(9 * s))),
                               fill="#94A3B8")

    def _draw_input(self, canvas, cx, y, word, pos, cell=30, max_w=None):
        n = len(word)
        if n == 0:
            canvas.create_text(cx, y + cell / 2, text="(vacia)",
                               font=("Segoe UI", 10, "italic"),
                               fill="#94A3B8")
            return
        if max_w is None:
            max_w = canvas.winfo_width() - 30
        cell = max(6, min(cell, max_w / n))
        x0 = max(6, cx - (n * cell) / 2)
        size = max(7, min(13, int(cell * 0.45)))
        for i, c in enumerate(word):
            x = x0 + i * cell
            is_cur = (i == pos)
            fill = "#FACC15" if is_cur else "#334155"
            tc = "#0F172A" if is_cur else "#F1F5F9"
            canvas.create_rectangle(x, y, x + cell, y + cell,
                                    fill=fill, outline="#F1F5F9")
            if cell >= 9:
                canvas.create_text(x + cell / 2, y + cell / 2,
                                   text=c,
                                   font=("Consolas", size, "bold"),
                                   fill=tc)

    def _hint_start(self, canvas, w, y):
        canvas.create_text(
            w / 2, y, text="Elige un ejemplo o escribe una cadena y pulsa Iniciar",
            font=("Segoe UI", 10, "italic"), fill="#94A3B8")

    def _draw_tape(self, canvas, cx, cy, tape, head,
                   cell_w=44, cell_h=48, blank="B"):
        n = len(tape)
        max_w = canvas.winfo_width() - 40
        if max_w > 100 and n * cell_w > max_w:
            cell_w = max(10, max_w // n)
        font_size = max(7, min(15, int(cell_w * 0.34)))

        total = n * cell_w
        x0 = max(6, cx - total / 2)
        y0 = cy - cell_h / 2

        for i, sym in enumerate(tape):
            x = x0 + i * cell_w
            is_head = (i == head)
            is_bound = (sym == "#")
            is_blank = (sym == blank)
            if is_head:
                fill, tc = "#FACC15", "#0F172A"
            elif is_bound:
                fill, tc = "#7C3AED", "#F1F5F9"
            elif is_blank:
                fill, tc = "#1E293B", "#64748B"
            else:
                fill, tc = "#334155", "#F1F5F9"
            canvas.create_rectangle(x, y0, x + cell_w, y0 + cell_h,
                                    fill=fill, outline="#F1F5F9",
                                    width=2)
            canvas.create_text(x + cell_w / 2, y0 + cell_h / 2,
                               text=sym,
                               font=("Consolas", font_size, "bold"),
                               fill=tc)
            if cell_w >= 16:
                canvas.create_text(x + cell_w / 2, y0 + cell_h + 12,
                                   text=str(i),
                                   font=("Segoe UI", 8), fill="#94A3B8")

        if 0 <= head < n:
            hx = x0 + head * cell_w + cell_w / 2
            canvas.create_polygon(
                hx, y0 - 6, hx - 10, y0 - 26, hx + 10, y0 - 26,
                fill="#FACC15",
            )
            canvas.create_text(hx, y0 - 36, text="cabezal",
                               font=("Segoe UI", 9, "bold"),
                               fill="#FACC15")

    def module_afd(self):
        ui = self.create_module(
            "AFD",
            "NIVEL 3 - AFD",
            "Lenguaje regular: cadenas binarias que terminan en 01",
            ["1101", "01", "0001", "10", "100", "1010"],
            "01",
            "Ingresa una cadena no vacia formada por 0 y 1.\n"
            "Ejemplos validos: 01, 1101, 1110, 100, ...",
            validator=lambda w: w.endswith("01"),
            alert_text="La cadena no termina en 01.",
        )
        entry, info, display = ui.entry, ui.info, ui.display
        write, clear_log, canvas = ui.write, ui.clear_log, ui.canvas

        transitions = {
            "q0": {"0": "q1", "1": "q0"},
            "q1": {"0": "q1", "1": "q2"},
            "q2": {"0": "q1", "1": "q0"},
        }

        state = {
            "word": "",
            "position": 0,
            "current": "q0",
            "finished": False,
        }

        def draw():
            ui.sync(state)
            canvas.delete("all")
            w, h = self._size(canvas)
            s = self._scale(w, h)
            r = int(34 * s)

            top, bottom = 10, h - 66
            loop_h = 46 * s
            up = r + loop_h + 26 * s
            depth = max(r + 14,
                        min(130 * s, (bottom - top) - up - 20 * s))
            down = depth + 20 * s
            free = (bottom - top) - (up + down)
            y0 = top + up + max(0, free / 2)

            pos = {
                "q0": (w * 0.17, y0),
                "q1": (w * 0.50, y0),
                "q2": (w * 0.83, y0),
            }
            rad = {"q0": r, "q1": r, "q2": r + 6}
            pair = 38 * s

            self._edge(canvas, pos["q0"], pos["q1"], rad["q0"], rad["q1"],
                       "0", 0, s)
            self._edge(canvas, pos["q1"], pos["q2"], rad["q1"], rad["q2"],
                       "1", pair, s)
            self._edge(canvas, pos["q2"], pos["q1"], rad["q2"], rad["q1"],
                       "0", pair, s)
            self._edge(canvas, pos["q2"], pos["q0"], rad["q2"], rad["q0"],
                       "1", 2 * depth, s)
            self._loop(canvas, pos["q0"], r, "1", loop_h, s)
            self._loop(canvas, pos["q1"], r, "0", loop_h, s)

            for name, c in pos.items():
                self._node(canvas, c, r, name, name == state["current"],
                           accepting=(name == "q2"), s=s)
            self._start_arrow(canvas, pos["q0"], r, s)

            if state["word"]:
                self._draw_input(canvas, w / 2, h - 58,
                                 state["word"], state["position"],
                                 cell=int(30 * s))
            else:
                self._hint_start(canvas, w, h - 44)

        def render():
            draw()
            display.config(
                text=(
                    f"Cadena: {state['word']}   "
                    f"Procesado: {state['word'][:state['position']]}   "
                    f"Estado actual: {state['current']}   "
                    f"(final: q2)"
                )
            )

        def reset_state(word):
            state.update({
                "word": word,
                "position": 0,
                "current": "q0",
                "finished": False,
            })
            clear_log()
            info.config(text="Simulacion iniciada", fg=self.accent)
            write("Estado inicial: q0")
            render()

        def start():
            ui.begin(reset_state)

        def restart():
            if state["word"]:
                reset_state(state["word"])

        def step():
            if not state["word"] or state["finished"]:
                return
            if state["position"] >= len(state["word"]):
                accepted = (state["current"] == "q2")
                info.config(
                    text="CADENA ACEPTADA" if accepted
                    else "CADENA RECHAZADA",
                    fg="#4ADE80" if accepted else "#F87171",
                )
                write("Resultado: " +
                      ("ACEPTADA" if accepted else "RECHAZADA"))
                state["finished"] = True
                draw()
                return
            symbol = state["word"][state["position"]]
            previous = state["current"]
            state["current"] = transitions[previous][symbol]
            state["position"] += 1
            write(f"Lee '{symbol}': {previous} -> {state['current']}")
            render()

        def clear_all():
            state.update({
                "word": "",
                "position": 0,
                "current": "q0",
                "finished": False,
            })
            clear_log()
            info.config(text="Preparado para iniciar la simulacion",
                        fg=self.accent)
            render()
            display.config(text="")
            entry.delete(0, "end")
            entry.focus_set()

        canvas.bind("<Configure>", lambda e: draw())
        ui.build_controls("Siguiente simbolo", start, restart, step,
                          clear_all)
        render()

    def module_pda(self):
        def is_anbn(w):
            n = len(w) // 2
            return n >= 1 and len(w) % 2 == 0 and w == "a" * n + "b" * n

        ui = self.create_module(
            "PDA",
            "NIVEL 2 - PDA",
            "Automata de pila: lenguaje a^n b^n",
            ["aaabbb", "ab", "aabb", "aba", "abab", "ba"],
            "ab",
            "Utiliza una cadena no vacia con simbolos a y b.\n"
            "Ejemplos validos: ab, aabb, aaabbb, ba, abab, ...",
            validator=is_anbn,
            alert_text="La cadena no cumple el patron a^n b^n.",
        )
        entry, info, display = ui.entry, ui.info, ui.display
        write, clear_log, canvas = ui.write, ui.clear_log, ui.canvas

        state = {
            "word": "",
            "position": 0,
            "stack": ["Z0"],
            "phase": "PUSH",
            "finished": False,
            "valid": True,
            "seen_b": False,
        }

        def current_state():
            if state.get("finished"):
                return "qA" if state.get("valid") else "q1"
            return "q0" if state.get("phase") == "PUSH" else "q1"

        def draw():
            ui.sync(state)
            canvas.delete("all")
            w, h = self._size(canvas)
            s = self._scale(w, h)
            r = int(28 * s)

            top, bottom = 10, h - 66
            loop_h = 44 * s
            up = r + loop_h + 26 * s
            down = r + 6
            free = (bottom - top) - (up + down)
            y0 = top + up + max(0, min(free / 2, 40 * s))

            pos = {
                "q0": (w * 0.11, y0),
                "q1": (w * 0.33, y0),
                "qA": (w * 0.55, y0),
            }
            rad = {"q0": r, "q1": r, "qA": r + 6}

            self._loop(canvas, pos["q0"], r, "a, push A", loop_h, s)
            self._loop(canvas, pos["q1"], r, "b, pop A", loop_h, s)
            self._edge(canvas, pos["q0"], pos["q1"], rad["q0"], rad["q1"],
                       "b, pop A", 0, s)
            self._edge(canvas, pos["q1"], pos["qA"], rad["q1"], rad["qA"],
                       "e, Z", 0, s)

            cur = current_state()
            for name, c in pos.items():
                self._node(canvas, c, r, name, name == cur,
                           accepting=(name == "qA"), s=s)
            self._start_arrow(canvas, pos["q0"], r, s, label=False)

            cell_w = max(70, 100 * s)
            stack_x = w * 0.83
            stack_bottom = h - 22
            stack_top = 40
            stack = state["stack"]
            cell_h = min(30, (stack_bottom - stack_top) / max(len(stack), 1))

            canvas.create_text(
                stack_x, 18, text="Pila (tope arriba)",
                font=("Segoe UI", max(8, int(10 * s)), "bold"),
                fill="#94A3B8",
            )
            for i, sym in enumerate(stack):
                cy = stack_bottom - i * cell_h
                is_top = (i == len(stack) - 1)
                fill = "#FACC15" if is_top else "#334155"
                tc = "#0F172A" if is_top else "#F1F5F9"
                canvas.create_rectangle(
                    stack_x - cell_w / 2, cy - cell_h,
                    stack_x + cell_w / 2, cy,
                    fill=fill, outline="#F1F5F9", width=1,
                )
                if cell_h >= 15:
                    canvas.create_text(
                        stack_x, cy - cell_h / 2,
                        text=sym,
                        font=("Consolas", max(7, min(13, int(cell_h * 0.42))),
                              "bold"),
                        fill=tc,
                    )

            strip_w = max(100, stack_x - cell_w / 2 - 40)
            if state["word"]:
                self._draw_input(canvas, 15 + strip_w / 2, h - 58,
                                 state["word"], state["position"],
                                 cell=int(30 * s), max_w=strip_w)
            else:
                canvas.create_text(
                    15 + strip_w / 2, h - 44,
                    text="Elige un ejemplo o escribe una cadena y pulsa Iniciar",
                    font=("Segoe UI", 10, "italic"), fill="#94A3B8")

        def render():
            draw()
            stack = state["stack"]
            cur = current_state()
            display.config(
                text=(
                    f"Cadena: {state['word']}   "
                    f"Estado: {cur}   "
                    f"Fase: {state['phase']}   "
                    f"Pila: {stack}"
                )
            )

        def reset_state(word):
            state.clear()
            state.update({
                "word": word,
                "position": 0,
                "stack": ["Z0"],
                "phase": "PUSH",
                "finished": False,
                "valid": True,
                "seen_b": False,
            })
            clear_log()
            info.config(text="Pila inicializada", fg=self.accent)
            write("Pila inicial: Z0")
            render()

        def start():
            ui.begin(reset_state)

        def restart():
            if state["word"]:
                reset_state(state["word"])

        def reject(reason):
            state["finished"] = True
            state["valid"] = False
            info.config(text="CADENA RECHAZADA", fg="#F87171")
            write("Rechazo: " + reason)
            draw()

        def step():
            if not state["word"] or state["finished"]:
                return
            word = state["word"]
            pos = state["position"]
            if pos >= len(word):
                accepted = (state["stack"] == ["Z0"]
                            and state["seen_b"])
                state["finished"] = True
                info.config(
                    text="CADENA ACEPTADA" if accepted
                    else "CADENA RECHAZADA",
                    fg="#4ADE80" if accepted else "#F87171",
                )
                write("La cadena fue aceptada."
                      if accepted else
                      "La pila no termino correctamente.")
                draw()
                return
            symbol = word[pos]
            if symbol == "a":
                if state["phase"] == "POP":
                    reject("No se permiten a despues de b.")
                    return
                state["stack"].append("A")
                write(f"Lee a: PUSH A -> {state['stack']}")
            elif symbol == "b":
                if len(state["stack"]) == 1:
                    reject("No hay elementos para desapilar.")
                    return
                state["phase"] = "POP"
                state["seen_b"] = True
                state["stack"].pop()
                write(f"Lee b: POP A -> {state['stack']}")
            else:
                reject("Simbolo no permitido.")
                return
            state["position"] += 1
            render()

        def clear_all():
            state.clear()
            state.update({
                "word": "",
                "position": 0,
                "stack": ["Z0"],
                "phase": "PUSH",
                "finished": False,
                "valid": True,
                "seen_b": False,
            })
            clear_log()
            info.config(text="Preparado para iniciar la simulacion",
                        fg=self.accent)
            render()
            display.config(text="")
            entry.delete(0, "end")
            entry.focus_set()

        canvas.bind("<Configure>", lambda e: draw())
        ui.build_controls("Siguiente simbolo", start, restart, step,
                          clear_all)
        render()

    def module_lba(self):
        def is_anbncn(w):
            n = len(w) // 3
            return (n >= 1 and len(w) % 3 == 0
                    and w == "a" * n + "b" * n + "c" * n)

        ui = self.create_module(
            "LBA",
            "NIVEL 1 - LBA",
            "Automata linealmente acotado: lenguaje a^n b^n c^n",
            ["aabbcc", "abc", "aaabbbccc", "abcc", "aabbc", "cba"],
            "abc",
            "Ingresa una cadena no vacia con a, b y c.\n"
            "Ejemplos validos: abc, aabbcc, aaabbbccc, cba, ...",
            validator=is_anbncn,
            alert_text="La cadena no cumple el patron a^n b^n c^n.",
        )
        entry, info, display = ui.entry, ui.info, ui.display
        write, clear_log, canvas = ui.write, ui.clear_log, ui.canvas

        state = {"word": "", "tape": [], "head": 0, "phase": "q0",
                 "finished": False, "accepted": False, "steps": 0}

        def draw():
            ui.sync(state)
            canvas.delete("all")
            w, h = self._size(canvas)
            s = self._scale(w, h)

            if not state["tape"]:
                self._hint_start(canvas, w, h / 2)
                return

            tape = state["tape"]
            head = state["head"]

            phase = state["phase"]
            if state.get("finished"):
                phase_txt = "qA (aceptacion)" if state.get("accepted") \
                            else "qR (rechazo)"
            else:
                phase_txt = phase

            canvas.create_text(
                15, 15, anchor="nw",
                text=f"Estado: {phase_txt}    "
                     f"Cabezal: {head}",
                font=("Segoe UI", 12, "bold"),
                fill="#F1F5F9",
            )
            canvas.create_text(
                15, h - 20, anchor="sw",
                text="Cinta acotada por # (fronteras)",
                font=("Segoe UI", 9, "italic"),
                fill="#94A3B8",
            )

            self._draw_tape(canvas, w / 2, h / 2 + 15, tape, head,
                            cell_w=int(44 * s), cell_h=int(48 * s))

        def render():
            draw()
            display.config(
                text=(
                    f"Entrada original: {state['word']}   "
                    f"Cinta: {''.join(state['tape'])}   "
                    f"Cabezal: {state['head']}   "
                    f"Fase: {state['phase']}"
                )
            )

        def reset_state(word):
            state.clear()
            state.update({
                "word": word,
                "tape": ["#", *list(word), "#"],
                "head": 1,
                "phase": "q0",
                "finished": False,
                "accepted": False,
                "steps": 0,
            })
            clear_log()
            info.config(text="Cinta delimitada e inicializada",
                        fg=self.accent)
            write("Inicio: cinta con fronteras # y cabezal en la primera celda (q0).")
            render()

        def start():
            ui.begin(reset_state)

        def restart():
            if state["word"]:
                reset_state(state["word"])

        def finish(accepted, reason):
            state["finished"] = True
            state["accepted"] = accepted
            state["phase"] = "qA" if accepted else "qR"
            info.config(
                text="CADENA ACEPTADA" if accepted
                else "CADENA RECHAZADA",
                fg="#4ADE80" if accepted else "#F87171",
            )
            write(reason)
            draw()

        def step():
            if not state["word"] or state["finished"]:
                return
            tape = state["tape"]
            head = state["head"]
            phase = state["phase"]
            symbol = tape[head]
            state["steps"] += 1
            ops = []

            def go(move, new_phase, mark=None):
                if mark is not None:
                    tape[head] = mark
                    ops.append(f"Marca {mark}")
                if move:
                    state["head"] += move
                    ops.append("Mueve a la derecha" if move > 0
                               else "Mueve a la izquierda")
                state["phase"] = new_phase

            if phase == "q0":
                if symbol == "A":
                    go(1, "q0")
                elif symbol == "a":
                    go(1, "q1", "A")
                elif symbol in ("B", "C", "#"):
                    go(0, "q4")
                else:
                    finish(False, "No se encontro una a valida.")
                    return

            elif phase == "q1":
                if symbol in ("A", "a", "B"):
                    go(1, "q1")
                elif symbol == "b":
                    go(1, "q2", "B")
                else:
                    finish(False, "Falta una b correspondiente.")
                    return

            elif phase == "q2":
                if symbol in ("B", "b", "C"):
                    go(1, "q2")
                elif symbol == "c":
                    go(-1, "q3", "C")
                else:
                    finish(False, "Falta una c correspondiente.")
                    return

            elif phase == "q3":
                if symbol == "#":
                    go(1, "q0")
                else:
                    go(-1, "q3")

            elif phase == "q4":
                if symbol in ("A", "B", "C"):
                    go(1, "q4")
                elif symbol == "#":
                    finish(True, "Final (qA): todas las letras fueron "
                                 "emparejadas.")
                    return
                else:
                    finish(False, "Quedaron letras sin emparejar.")
                    return

            if not (0 <= state["head"] < len(tape)):
                finish(False, "Se intento salir de los limites.")
                return

            detail = " | ".join(ops) if ops else "Sin mover"
            write(
                f"Paso {state['steps']}: "
                f"{phase} -> {state['phase']} | "
                f"Lee {symbol} | {detail} | Cabezal {state['head']}"
            )
            render()

        def clear_all():
            state.clear()
            state.update({"word": "", "tape": [], "head": 0, "phase": "q0",
                          "finished": False, "accepted": False, "steps": 0})
            clear_log()
            info.config(text="Preparado para iniciar la simulacion",
                        fg=self.accent)
            render()
            display.config(text="")
            entry.delete(0, "end")
            entry.focus_set()

        canvas.bind("<Configure>", lambda e: draw())
        ui.build_controls("Siguiente transicion", start, restart, step,
                          clear_all)
        render()

    def module_tm(self):
        ui = self.create_module(
            "TM",
            "NIVEL 0 - MAQUINA DE TURING",
            "Operacion aritmetica: incremento en representacion unaria",
            ["111", "1", "11", "1111", "11111"],
            "1",
            "Ingresa un numero unario usando solamente 1.\n"
            "Ejemplos validos: 1, 11, 111, 1111, ...",
        )
        entry, info, display = ui.entry, ui.info, ui.display
        write, clear_log, canvas = ui.write, ui.clear_log, ui.canvas

        state = {"word": "", "tape": [], "head": 0, "phase": "q0",
                 "finished": False, "result": "-"}

        def draw():
            ui.sync(state)
            canvas.delete("all")
            w, h = self._size(canvas)
            s = self._scale(w, h)

            if not state["tape"]:
                self._hint_start(canvas, w, h / 2)
                return

            tape = state["tape"]
            head = state["head"]
            phase = state["phase"]

            canvas.create_text(
                15, 15, anchor="nw",
                text=f"Estado: {phase}    Cabezal: {head}    "
                     f"Alfabeto: {{1, B}}",
                font=("Segoe UI", 12, "bold"),
                fill="#F1F5F9",
            )
            canvas.create_text(
                15, h - 20, anchor="sw",
                text="Cinta extendible (se llena de B a la derecha)",
                font=("Segoe UI", 9, "italic"),
                fill="#94A3B8",
            )

            self._draw_tape(canvas, w / 2, h / 2 + 15, tape, head,
                            cell_w=int(44 * s), cell_h=int(48 * s),
                            blank="B")

        def render():
            draw()
            display.config(
                text=(
                    f"Cinta: {''.join(state['tape'])}   "
                    f"Cabezal: {state['head']}   "
                    f"Estado: {state['phase']}   "
                    f"Resultado: {state.get('result', '-')}"
                )
            )

        def reset_state(word):
            state.clear()
            state.update({
                "word": word,
                "tape": list(word) + ["B", "B", "B"],
                "head": 0,
                "phase": "q0",
                "finished": False,
                "result": "-",
            })
            clear_log()
            info.config(text="Maquina preparada", fg=self.accent)
            write("Estado inicial: q0")
            render()

        def start():
            ui.begin(reset_state)

        def restart():
            if state["word"]:
                reset_state(state["word"])

        def step():
            if not state["word"] or state["finished"]:
                return
            head = state["head"]
            tape = state["tape"]
            phase = state["phase"]

            if phase == "q0":
                if tape[head] == "1":
                    write(f"Lee 1 en {head}. Se mueve a la derecha.")
                    state["head"] += 1
                elif tape[head] == "B":
                    tape[head] = "1"
                    state["phase"] = "qA"
                    result = "".join(tape).rstrip("B")
                    state["result"] = result
                    state["finished"] = True
                    info.config(
                        text="OPERACION COMPLETADA",
                        fg="#4ADE80",
                    )
                    write("Se escribe 1 en la primera posicion vacia.")
                    write("La maquina alcanza el estado final qA.")
                    write(f"Resultado: {result}")

            render()

        def clear_all():
            state.clear()
            state.update({"word": "", "tape": [], "head": 0, "phase": "q0",
                          "finished": False, "result": "-"})
            clear_log()
            info.config(text="Preparado para iniciar la simulacion",
                        fg=self.accent)
            render()
            display.config(text="")
            entry.delete(0, "end")
            entry.focus_set()

        canvas.bind("<Configure>", lambda e: draw())
        ui.build_controls("Siguiente movimiento", start, restart, step,
                          clear_all)
        render()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChomskyLab(root)
    root.mainloop()