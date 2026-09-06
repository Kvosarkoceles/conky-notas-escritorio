#!/usr/bin/env python3
import json
import os
import tkinter as tk
from tkinter import messagebox

APP_DIR = os.path.expanduser("~/.desktop-notes")
DATA_FILE = os.path.join(APP_DIR, "notes.json")

DEFAULT = [
    {
        "title": "Bienvenido",
        "body": "Doble clic sobre una nota para editarla.\nPulsa + para crear una nueva.",
        "x": 0,
        "y": 0
    }
]

os.makedirs(APP_DIR, exist_ok=True)

def load_notes():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else DEFAULT.copy()
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return DEFAULT.copy()

def save_notes():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
        return True
    except OSError as exc:
        messagebox.showerror("Notas", f"No se pudo guardar:\n\n{exc}")
        return False


class ModernButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        normal_background = kwargs.get("bg", "#303134")
        hover_background = kwargs.get(
            "activebackground",
            normal_background
        )
        super().__init__(master, **kwargs)
        self.configure(
            relief="flat",
            overrelief="flat",
            borderwidth=0,
            highlightthickness=0,
            activeforeground="#ffffff"
        )
        self.bind(
            "<Enter>",
            lambda event: self.configure(bg=hover_background),
            add="+"
        )
        self.bind(
            "<Leave>",
            lambda event: self.configure(bg=normal_background),
            add="+"
        )


class IconButton(ModernButton):
    def __init__(self, master=None, tooltip="", **kwargs):
        self.tooltip_text = tooltip
        self.tooltip_window = None
        self.tooltip_after_id = None
        kwargs.setdefault("width", 3)
        kwargs.setdefault("height", 1)
        kwargs.setdefault("padx", 0)
        kwargs.setdefault("pady", 0)
        kwargs.setdefault("font", ("Sans", 13, "bold"))
        super().__init__(master, **kwargs)
        self.bind("<Enter>", self._schedule_tooltip, add="+")
        self.bind("<Leave>", self._hide_tooltip, add="+")

    def _schedule_tooltip(self, _event):
        if self.tooltip_text:
            self.tooltip_after_id = self.after(450, self._show_tooltip)

    def _show_tooltip(self):
        if self.tooltip_window or not self.winfo_exists():
            return
        self.tooltip_window = tk.Toplevel(self)
        self.tooltip_window.overrideredirect(True)
        self.tooltip_window.attributes("-topmost", True)
        tk.Label(
            self.tooltip_window,
            text=self.tooltip_text,
            bg="#111827",
            fg="#f8fafc",
            padx=8,
            pady=4,
            font=("Sans", 9)
        ).pack()
        self.tooltip_window.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2)
        y = self.winfo_rooty() + self.winfo_height() + 6
        self.tooltip_window.geometry(f"+{x}+{y}")

    def _hide_tooltip(self, _event):
        if self.tooltip_after_id:
            self.after_cancel(self.tooltip_after_id)
            self.tooltip_after_id = None
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class NoteEditor(tk.Toplevel):
    def __init__(self, master, index=None):
        super().__init__(master)
        self.master_app = master
        self.index = index
        self.title("Editar nota" if index is not None else "Nueva nota")
        self.geometry("500x420")
        self.minsize(400, 320)
        self.configure(bg="#202124")
        self.transient(master)
        self.attributes("-topmost", True)

        # Encabezado
        header = tk.Frame(self, bg="#202124", padx=18, pady=12)
        header.pack(fill="x")

        tk.Label(
            header,
            text="✎ EDITAR NOTA" if index is not None else "✚ NUEVA NOTA",
            fg="#ffffff",
            bg="#202124",
            font=("Sans", 12, "bold")
        ).pack(anchor="w")

        content = tk.Frame(self, bg="#202124", padx=18)
        content.pack(fill="both", expand=True)

        tk.Label(
            content, text="Título",
            fg="#e8eaed", bg="#202124",
            font=("Sans", 10, "bold")
        ).pack(anchor="w")

        self.title_var = tk.StringVar()
        self.title_entry = tk.Entry(
            content,
            textvariable=self.title_var,
            bg="#303134",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief="flat",
            font=("Sans", 11)
        )
        self.title_entry.pack(fill="x", pady=(5, 14), ipady=8)

        tk.Label(
            content, text="Contenido",
            fg="#e8eaed", bg="#202124",
            font=("Sans", 10, "bold")
        ).pack(anchor="w")

        text_frame = tk.Frame(content, bg="#303134")
        text_frame.pack(fill="both", expand=True, pady=(5, 14))

        self.text = tk.Text(
            text_frame,
            bg="#303134",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief="flat",
            wrap="word",
            font=("Sans", 11),
            padx=10,
            pady=10
        )
        self.text.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(text_frame, command=self.text.yview)
        scrollbar.pack(side="right", fill="y")
        self.text.config(yscrollcommand=scrollbar.set)

        # Barra de botones SIEMPRE visible
        footer = tk.Frame(
            self,
            bg="#18191a",
            height=58,
            padx=18,
            pady=8
        )
        content.pack_configure(pady=(0, 58))
        footer.place(relx=0, rely=1, anchor="sw", relwidth=1, height=58)
        footer.pack_propagate(False)

        if index is not None:
            IconButton(
                footer,
                text="🗑",
                tooltip="Eliminar nota",
                command=self.delete_note,
                bg="#7b2424",
                fg="#ffffff",
                activebackground="#9a3030",
                activeforeground="#ffffff",
                relief="flat",
                cursor="hand2"
            ).pack(side="left")

        IconButton(
            footer,
            text="×",
            tooltip="Cancelar",
            command=self.destroy,
            bg="#3c4043",
            fg="#ffffff",
            activebackground="#4b4f52",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2"
        ).pack(side="right", padx=(8, 0))

        self.save_button = IconButton(
            footer,
            text="💾",
            tooltip="Guardar cambios",
            command=self.save,
            bg="#1a73e8",
            fg="#ffffff",
            activebackground="#4285f4",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2"
        )
        self.save_button.pack(side="right")

        if index is not None:
            note = notes[index]
            self.title_var.set(note.get("title", "Sin título"))
            self.text.insert("1.0", note.get("body", ""))

        self.title_entry.focus_set()
        self.after_idle(self._activate)

        # Ctrl+S / Enter en título
        self.bind("<Control-s>", lambda event: self.save())
        self.title_entry.bind("<Control-s>", lambda event: self.save())
        self.bind("<Escape>", lambda event: self.destroy())

    def _activate(self):
        if self.winfo_exists() and self.winfo_viewable():
            self.grab_set()
            self.focus_force()
            self.title_entry.focus_set()

    def save(self):
        title = self.title_var.get().strip() or "Sin título"
        body = self.text.get("1.0", "end-1c").rstrip()

        item = {
            "title": title,
            "body": body,
            "x": 0,
            "y": 0
        }

        if self.index is None:
            notes.append(item)
        else:
            notes[self.index].update(item)

        if save_notes():
            self.master_app.refresh()
            self.destroy()

    def delete_note(self):
        if self.index is None:
            self.destroy()
            return

        notes.pop(self.index)
        if save_notes():
            self.master_app.refresh()
            self.destroy()


class NotesApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Mis notas")
        self.configure(bg="#18191a")
        self.lower()
        self.bind("<Map>", lambda event: self.lower())
        self.bind("<Visibility>", lambda event: self.lower())
        self._keep_below()

        width = 350
        height = 470
        screen_w = self.winfo_screenwidth()
        x = max(0, screen_w - width - 18)
        y = 120
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Encabezado
        self.header = tk.Frame(
            self,
            bg="#202124",
            height=48
        )
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        title = tk.Label(
            self.header,
            text="📝  MIS NOTAS",
            fg="#ffffff",
            bg="#202124",
            font=("Sans", 11, "bold")
        )
        title.pack(side="left", padx=12)

        IconButton(
            self.header,
            text="✕",
            tooltip="Cerrar aplicación",
            command=self.destroy,
            fg="#ffffff",
            bg="#7b2424",
            activebackground="#9a3030",
            activeforeground="#ffffff",
            relief="flat",
            width=3,
            cursor="hand2"
        ).pack(side="right", padx=(0, 6), pady=6)

        IconButton(
            self.header,
            text="＋",
            tooltip="Nueva nota",
            command=self.new_note,
            fg="#ffffff",
            bg="#1a73e8",
            activebackground="#4285f4",
            activeforeground="#ffffff",
            relief="flat",
            width=3,
            cursor="hand2"
        ).pack(side="right", padx=6, pady=6)

        # Área de notas
        self.body = tk.Frame(
            self,
            bg="#18191a",
            padx=8,
            pady=8
        )
        self.body.pack(fill="both", expand=True)

        self.refresh()

        # Arrastrar panel desde la cabecera
        for widget in (self.header, title):
            widget.bind("<ButtonPress-1>", self.start_move)
            widget.bind("<B1-Motion>", self.do_move)

        self.bind("<Escape>", lambda event: self.destroy())

    def start_move(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def do_move(self, event):
        x = self.winfo_x() + event.x - self._drag_x
        y = self.winfo_y() + event.y - self._drag_y
        self.geometry(f"+{x}+{y}")

    def _keep_below(self):
        self.lower()
        self.after(1000, self._keep_below)

    def refresh(self):
        for widget in self.body.winfo_children():
            widget.destroy()

        if not notes:
            tk.Label(
                self.body,
                text="No hay notas.\n\nPulsa  +  para crear una.",
                fg="#9aa0a6",
                bg="#18191a",
                font=("Sans", 10),
                justify="center"
            ).pack(expand=True)
            return

        for i, note in enumerate(notes):
            card = tk.Frame(
                self.body,
                bg="#292a2d",
                padx=10,
                pady=9,
                cursor="hand2"
            )
            card.pack(fill="x", pady=4)

            title = tk.Label(
                card,
                text=note.get("title", "Sin título"),
                fg="#ffffff",
                bg="#292a2d",
                font=("Sans", 10, "bold"),
                anchor="w",
                cursor="hand2"
            )
            title.pack(fill="x")

            body = note.get("body", "")
            preview = body.replace("\n", " ")
            if len(preview) > 110:
                preview = preview[:110].rstrip() + "…"

            desc = tk.Label(
                card,
                text=preview,
                fg="#bdc1c6",
                bg="#292a2d",
                font=("Sans", 9),
                justify="left",
                anchor="w",
                wraplength=300,
                cursor="hand2"
            )
            desc.pack(fill="x", pady=(4, 0))

            actions = tk.Frame(card, bg="#292a2d")
            actions.pack(fill="x", pady=(8, 0))

            IconButton(
                actions,
                text="✎",
                tooltip="Editar nota",
                command=lambda idx=i: self.edit_note(idx),
                bg="#1a73e8",
                fg="#ffffff",
                activebackground="#4285f4",
                activeforeground="#ffffff",
                relief="flat",
                cursor="hand2"
            ).pack(side="left")

            IconButton(
                actions,
                text="🗑",
                tooltip="Eliminar nota",
                command=lambda idx=i: self.delete_note(idx),
                bg="#7b2424",
                fg="#ffffff",
                activebackground="#9a3030",
                activeforeground="#ffffff",
                relief="flat",
                cursor="hand2"
            ).pack(side="right")

            for widget in (card, title, desc):
                widget.bind(
                    "<Double-Button-1>",
                    lambda event, idx=i: self.edit_note(idx)
                )
                widget.bind(
                    "<Button-1>",
                    lambda event, selected=card: self.select_card(selected)
                )

    def select_card(self, card):
        for child in self.body.winfo_children():
            try:
                child.configure(bg="#292a2d")
                for sub in child.winfo_children():
                    sub.configure(bg="#292a2d")
            except tk.TclError:
                pass

        try:
            card.configure(bg="#3c4043")
            for sub in card.winfo_children():
                sub.configure(bg="#3c4043")
        except tk.TclError:
            pass

    def new_note(self):
        NoteEditor(self)

    def edit_note(self, index):
        NoteEditor(self, index)

    def delete_note(self, index):
        notes.pop(index)
        if save_notes():
            self.refresh()


if __name__ == "__main__":
    notes = load_notes()
    app = NotesApp()
    app.mainloop()
