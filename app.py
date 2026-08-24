import json
import os
import re
import sys
import subprocess
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

from version import __version__


def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def untrim_frame(cropped, frame_data):
    """Restore a trimmed frame onto its full sourceSize canvas at its spriteSourceSize offset."""
    if not frame_data.get("trimmed"):
        return cropped
    source_size = frame_data.get("sourceSize")
    sprite_source_size = frame_data.get("spriteSourceSize")
    if not source_size or not sprite_source_size:
        return cropped
    canvas = Image.new("RGBA", (source_size["w"], source_size["h"]), (0, 0, 0, 0))
    canvas.paste(cropped, (sprite_source_size["x"], sprite_source_size["y"]))
    return canvas


def session_path():
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", str(Path.home())))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return base / "TextureSplitter" / "session.json"

if getattr(sys, "frozen", False):
    ICON_PATH = Path(sys._MEIPASS) / "favicon.png"
else:
    ICON_PATH = Path(__file__).parent / "assets" / "favicon.png"

AUTHOR = "saqirmdevx"
AUTHOR_URL = "https://github.com/saqirmdevx"
LANGS = {
    "pt": "🇧🇷 Português",
    "en": "🇺🇸 English",
    "es": "🇪🇸 Español",
    "zh": "🇨🇳 中文",
    "sk": "🇸🇰 Slovenčina",
}
MADE = {
    "pt": "Programa feito por:",
    "en": "Program made by:",
    "es": "Programa hecho por:",
    "zh": "程序制作人：",
    "sk": "Program vytvoril:",
}
T = {
    "pt": {
        "title": "TextureSplitter",
        "json": "JSON",
        "choose_json": "Selecionar JSON...",
        "size": "Escolha o tamanho do Sprite:",
        "original": "Original",
        "custom": "Personalizado...",
        "settings": "Configurações do JSON",
        "output": "Pasta de saída:",
        "choose_folder": "Selecionar pasta...",
        "cut": "✂  CORTAR IMAGENS",
        "preview": "Pré-visualização",
        "root_group": "Frames",
        "ready": "Pronto.",
        "select_sprite": "Selecione um sprite na pré-visualização.",
        "frame": "Frame",
        "anchor": "Âncora",
        "source": "Tamanho original",
        "sprite_source": "Tamanho no spritesheet",
        "rotated": "Rotacionado",
        "trimmed": "Recortado",
        "done": "Concluído! {n} imagens salvas.",
        "errjson": "Escolha o arquivo JSON.",
        "errout": "Escolha a pasta de saída.",
        "custom_title": "Tamanho personalizado",
        "custom_prompt": "Digite o tamanho do sprite (ex.: 64):",
        "invalid": "Digite um número inteiro maior que zero.",
        "play_anim": "▶ Reproduzir",
        "play": "Reproduzir",
        "pause": "Pausar",
        "stop": "Parar",
        "speed": "Velocidade:",
        "zoom": "Zoom:",
        "no_frames": "Nenhum sprite nesta pasta.",
    },
    "en": {
        "title": "TextureSplitter",
        "json": "JSON",
        "choose_json": "Select JSON...",
        "size": "Choose Sprite Size:",
        "original": "Original",
        "custom": "Custom...",
        "settings": "JSON Settings",
        "output": "Output folder:",
        "choose_folder": "Select folder...",
        "cut": "✂  CUT IMAGES",
        "preview": "Preview",
        "root_group": "Frames",
        "ready": "Ready.",
        "select_sprite": "Select a sprite in the preview.",
        "frame": "Frame",
        "anchor": "Anchor",
        "source": "Source size",
        "sprite_source": "Spritesheet size",
        "rotated": "Rotated",
        "trimmed": "Trimmed",
        "done": "Done! {n} images saved.",
        "errjson": "Choose the JSON file.",
        "errout": "Choose the output folder.",
        "custom_title": "Custom size",
        "custom_prompt": "Enter sprite size (e.g. 64):",
        "invalid": "Enter a positive integer.",
        "play_anim": "▶ Play",
        "play": "Play",
        "pause": "Pause",
        "stop": "Stop",
        "speed": "Speed:",
        "zoom": "Zoom:",
        "no_frames": "No sprites in this folder.",
    },
    "es": {
        "title": "TextureSplitter",
        "json": "JSON",
        "choose_json": "Seleccionar JSON...",
        "size": "Elige el tamaño del Sprite:",
        "original": "Original",
        "custom": "Personalizado...",
        "settings": "Configuración del JSON",
        "output": "Carpeta de salida:",
        "choose_folder": "Seleccionar carpeta...",
        "cut": "✂  CORTAR IMÁGENES",
        "preview": "Vista previa",
        "root_group": "Frames",
        "ready": "Listo.",
        "select_sprite": "Selecciona un sprite en la vista previa.",
        "frame": "Frame",
        "anchor": "Anclaje",
        "source": "Tamaño original",
        "sprite_source": "Tamaño en el spritesheet",
        "rotated": "Rotado",
        "trimmed": "Recortado",
        "done": "¡Listo! {n} imágenes guardadas.",
        "errjson": "Elige el archivo JSON.",
        "errout": "Elige la carpeta de salida.",
        "custom_title": "Tamaño personalizado",
        "custom_prompt": "Escribe el tamaño del sprite (ej.: 64):",
        "invalid": "Escribe un número entero mayor que cero.",
        "play_anim": "▶ Reproducir",
        "play": "Reproducir",
        "pause": "Pausar",
        "stop": "Detener",
        "speed": "Velocidad:",
        "zoom": "Zoom:",
        "no_frames": "No hay sprites en esta carpeta.",
    },
    "zh": {
        "title": "TextureSplitter",
        "json": "JSON",
        "choose_json": "选择 JSON...",
        "size": "选择 Sprite 大小：",
        "original": "原始大小",
        "custom": "自定义...",
        "settings": "JSON 设置",
        "output": "输出文件夹：",
        "choose_folder": "选择文件夹...",
        "cut": "✂  切割图像",
        "preview": "预览",
        "root_group": "帧",
        "ready": "就绪。",
        "select_sprite": "请在预览中选择一个 Sprite。",
        "frame": "Frame",
        "anchor": "锚点",
        "source": "原始大小",
        "sprite_source": "Spritesheet 大小",
        "rotated": "旋转",
        "trimmed": "裁剪",
        "done": "完成！已保存 {n} 张图片。",
        "errjson": "请选择 JSON 文件。",
        "errout": "请选择输出文件夹。",
        "custom_title": "自定义大小",
        "custom_prompt": "输入 Sprite 大小（例如 64）：",
        "invalid": "请输入大于零的整数。",
        "play_anim": "▶ 播放",
        "play": "播放",
        "pause": "暂停",
        "stop": "停止",
        "speed": "速度：",
        "zoom": "缩放：",
        "no_frames": "此文件夹中没有 Sprite。",
    },
    "sk": {
        "title": "TextureSplitter",
        "json": "JSON",
        "choose_json": "Vybrať JSON...",
        "size": "Vyberte veľkosť Sprite:",
        "original": "Pôvodná veľkosť",
        "custom": "Vlastná...",
        "settings": "Nastavenia JSON",
        "output": "Výstupný priečinok:",
        "choose_folder": "Vybrať priečinok...",
        "cut": "✂  ROZDELIŤ OBRÁZKY",
        "preview": "Náhľad",
        "root_group": "Snímky",
        "ready": "Pripravené.",
        "select_sprite": "Vyberte Sprite v náhľade.",
        "frame": "Frame",
        "anchor": "Kotva",
        "source": "Pôvodná veľkosť",
        "sprite_source": "Veľkosť v spritesheete",
        "rotated": "Otočené",
        "trimmed": "Orezané",
        "done": "Hotovo! Uložených obrázkov: {n}.",
        "errjson": "Vyberte JSON súbor.",
        "errout": "Vyberte výstupný priečinok.",
        "custom_title": "Vlastná veľkosť",
        "custom_prompt": "Zadajte veľkosť sprite (napr. 64):",
        "invalid": "Zadajte celé číslo väčšie ako nula.",
        "play_anim": "▶ Prehrať",
        "play": "Prehrať",
        "pause": "Pauza",
        "stop": "Zastaviť",
        "speed": "Rýchlosť:",
        "zoom": "Priblíženie:",
        "no_frames": "V tomto priečinku nie sú žiadne sprity.",
    },
}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang = "en"
        self.png = None
        self.json_path = None
        self.out = None
        self.anim_zoom = 1.0
        self.data = None
        self.sheet = None
        self.selected = None
        self.size = None
        self.original_mode = True
        self.thumbs = []
        self.bg = "#10151c"
        self.panel = "#191f28"
        self.panel2 = "#222a35"
        self.border = "#303a47"
        self.text = "#e8edf4"
        self.muted = "#7f8b9a"
        self.accent = "#70e6b5"
        self.geometry("1180x800")
        self.minsize(980, 650)
        self.configure(bg=self.bg)
        self.title("TextureSplitter")
        self._icon_image = ImageTk.PhotoImage(Image.open(ICON_PATH))
        self.iconphoto(True, self._icon_image)
        self.build()
        self.load_session()
        self.refresh()
        self.make_shortcut()

    def tr(self, k):
        return T[self.lang][k]

    def build(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure(
            "Dark.TButton",
            background=self.panel2,
            foreground=self.text,
            bordercolor=self.border,
            borderwidth=1,
            focuscolor=self.panel2,
            padding=6,
            font=("Segoe UI", 9),
        )
        style.map(
            "Dark.TButton",
            background=[("active", self.border), ("pressed", self.border)],
            foreground=[("active", self.accent)],
        )
        style.configure(
            "Cut.TButton",
            background="#317b61",
            foreground="white",
            bordercolor="#317b61",
            borderwidth=0,
            focuscolor="#317b61",
            padding=8,
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Cut.TButton",
            background=[("active", self.accent)],
            foreground=[("active", "#0b1016")],
        )
        style.configure(
            "TCombobox",
            fieldbackground=self.panel2,
            background=self.panel2,
            foreground=self.text,
            arrowcolor=self.text,
            bordercolor=self.border,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", self.panel2)],
            foreground=[("readonly", self.text)],
            selectbackground=[("readonly", self.panel2)],
            selectforeground=[("readonly", self.text)],
        )
        style.configure(
            "Vertical.TScrollbar",
            background=self.panel2,
            troughcolor=self.bg,
            bordercolor=self.border,
            arrowcolor=self.text,
        )
        self.style = style
        top = tk.Frame(self, bg=self.panel, height=50)
        top.pack(fill="x")
        top.pack_propagate(False)
        self.title_lbl = tk.Label(top, bg=self.panel, fg=self.text, font=("Segoe UI", 14, "bold"))
        self.title_lbl.pack(side="left", padx=16)
        self.lang_btn = ttk.Button(top, style="Dark.TButton", cursor="hand2", command=self.lang_menu)
        self.lang_btn.pack(side="right", padx=5)
        body = tk.Frame(self, bg=self.bg)
        body.pack(fill="both", expand=True, padx=16, pady=14)
        left = tk.Frame(body, bg=self.bg, width=380)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)
        left_canvas = tk.Canvas(left, bg=self.bg, highlightthickness=0)
        left_sb = ttk.Scrollbar(left, orient="vertical", command=left_canvas.yview)
        left_canvas.configure(yscrollcommand=left_sb.set)
        left_sb.pack(side="right", fill="y")
        left_canvas.pack(side="left", fill="both", expand=True)
        left_inner = tk.Frame(left_canvas, bg=self.bg)
        left_win = left_canvas.create_window((0, 0), window=left_inner, anchor="nw")
        left_inner.bind(
            "<Configure>", lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all"))
        )
        left_canvas.bind(
            "<Configure>", lambda e: left_canvas.itemconfigure(left_win, width=e.width)
        )
        right = tk.Frame(body, bg=self.bg)
        right.pack(side="left", fill="both", expand=True)
        files = tk.Frame(
            left_inner, bg=self.panel, highlightbackground=self.border, highlightthickness=1
        )
        files.pack(fill="x", pady=(0, 10))
        self.json_label = self.lab(files)
        self.json_label.pack(anchor="w", padx=14, pady=(12, 4))
        self.json_btn = self.btn(files, self.choose_json)
        self.json_btn.pack(fill="x", padx=14)
        self.json_var = tk.StringVar()
        tk.Label(
            files,
            textvariable=self.json_var,
            bg=self.panel,
            fg=self.muted,
            anchor="w",
            font=("Segoe UI", 8),
        ).pack(fill="x", padx=14, pady=4)
        self.png_var = tk.StringVar()
        tk.Label(
            files,
            textvariable=self.png_var,
            bg=self.panel,
            fg=self.muted,
            anchor="w",
            font=("Segoe UI", 8),
        ).pack(fill="x", padx=14, pady=(0, 4))
        self.size_label = self.lab(files)
        self.size_label.pack(anchor="w", padx=14, pady=(5, 4))
        self.size_var = tk.StringVar(value=self.tr("original"))
        self.combo = ttk.Combobox(
            files,
            textvariable=self.size_var,
            values=(
                self.tr("original"),
                "16 x 16",
                "32 x 32",
                "48 x 48",
                "64 x 64",
                "96 x 96",
                "128 x 128",
                "256 x 256",
                "512 x 512",
            ),
            state="readonly",
        )
        self.combo.pack(fill="x", padx=14)
        self.combo.bind("<<ComboboxSelected>>", self.size_changed)
        self.custom_btn = self.btn(files, self.custom_size)
        self.custom_btn.pack(fill="x", padx=14, pady=(5, 12))
        setp = tk.Frame(
            left_inner, bg=self.panel, highlightbackground=self.border, highlightthickness=1
        )
        setp.pack(fill="x", pady=(0, 10))
        self.settings_title = self.lab(setp)
        self.settings_title.pack(anchor="w", padx=14, pady=(12, 6))
        self.settings = tk.Text(
            setp,
            bg=self.panel2,
            fg=self.text,
            relief="flat",
            font=("Consolas", 9),
            wrap="word",
            height=11,
        )
        self.settings.pack(fill="x", padx=10, pady=(0, 10))
        self.settings.configure(state="disabled")
        outp = tk.Frame(
            left_inner, bg=self.panel, highlightbackground=self.border, highlightthickness=1
        )
        outp.pack(fill="x")
        self.out_label = self.lab(outp)
        self.out_label.pack(anchor="w", padx=14, pady=(10, 4))
        self.out_btn = self.btn(outp, self.choose_output)
        self.out_btn.pack(fill="x", padx=14)
        self.out_var = tk.StringVar()
        tk.Label(
            outp,
            textvariable=self.out_var,
            bg=self.panel,
            fg=self.muted,
            anchor="w",
            font=("Segoe UI", 8),
        ).pack(fill="x", padx=14, pady=4)
        self.cut_btn = ttk.Button(outp, style="Cut.TButton", cursor="hand2", command=self.cut)
        self.cut_btn.pack(fill="x", padx=14, pady=(8, 14))
        self._bind_wheel(left_canvas, left_canvas)
        prev = tk.Frame(right, bg=self.panel, highlightbackground=self.border, highlightthickness=1)
        prev.pack(fill="both", expand=True)
        self.prev_title = self.lab(prev)
        self.prev_title.pack(anchor="w", padx=14, pady=(12, 2))
        self.count = tk.Label(prev, bg=self.panel, fg=self.muted, font=("Segoe UI", 8))
        self.count.pack(anchor="w", padx=14, pady=(0, 6))
        self.canvas = tk.Canvas(prev, bg="#0b1016", highlightthickness=0)
        sb = ttk.Scrollbar(prev, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y", padx=(0, 8), pady=8)
        self.canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=8)
        self.inner = tk.Frame(self.canvas, bg="#0b1016")
        self.win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind(
            "<Configure>", lambda e: self.canvas.itemconfigure(self.win, width=e.width)
        )
        self._bind_wheel(self.canvas, self.canvas)
        self.status = tk.Label(
            self, bg="#0b1016", fg=self.muted, anchor="w", font=("Segoe UI", 8), padx=14
        )
        self.status.pack(fill="x", side="bottom")
        credit = tk.Frame(self, bg=self.bg)
        credit.pack(fill="x", side="bottom", pady=5)
        tk.Frame(credit, bg=self.bg).pack(side="left", expand=True)
        self.credit_prefix = tk.Label(credit, bg=self.bg, fg="#566171", font=("Segoe UI", 7))
        self.credit_prefix.pack(side="left")
        self.credit = tk.Label(
            credit, bg=self.bg, fg="#748297", font=("Segoe UI", 7, "underline"), cursor="hand2"
        )
        self.credit.pack(side="left")
        self.credit.bind("<Button-1>", lambda e: webbrowser.open(AUTHOR_URL))
        self.version_lbl = tk.Label(
            credit, bg=self.bg, fg="#566171", font=("Segoe UI", 7), text=f" · v{__version__}"
        )
        self.version_lbl.pack(side="left")
        tk.Frame(credit, bg=self.bg).pack(side="left", expand=True)

    def lab(self, p):
        return tk.Label(p, bg=self.panel, fg=self.text, font=("Segoe UI", 9, "bold"))

    def btn(self, p, cmd):
        return ttk.Button(p, style="Dark.TButton", cursor="hand2", command=cmd)

    def _bind_wheel(self, widget, canvas):
        def handler(e):
            if getattr(e, "num", None) == 4:
                units = -1
            elif getattr(e, "num", None) == 5:
                units = 1
            else:
                delta = e.delta
                units = int(-delta / 120) if abs(delta) >= 120 else (-1 if delta > 0 else 1)
            canvas.yview_scroll(max(-3, min(3, units)), "units")
            return "break"

        widget.bind("<MouseWheel>", handler)
        widget.bind("<Button-4>", handler)
        widget.bind("<Button-5>", handler)
        for child in widget.winfo_children():
            self._bind_wheel(child, canvas)

    def refresh(self):
        self.title_lbl.config(text="TextureSplitter")
        self.lang_btn.config(text="🌐 " + LANGS[self.lang])
        self.json_label.config(text="JSON")
        self.json_btn.config(text=self.tr("choose_json"))
        self.size_label.config(text=self.tr("size"))
        self.combo["values"] = (
            self.tr("original"),
            "16 x 16",
            "32 x 32",
            "48 x 48",
            "64 x 64",
            "96 x 96",
            "128 x 128",
            "256 x 256",
            "512 x 512",
        )
        if self.original_mode:
            self.size_var.set(self.tr("original"))
        self.custom_btn.config(text=self.tr("custom"))
        self.settings_title.config(text=self.tr("settings"))
        self.out_label.config(text=self.tr("output"))
        self.out_btn.config(text=self.tr("choose_folder"))
        self.cut_btn.config(text=self.tr("cut"))
        self.prev_title.config(text=self.tr("preview"))
        self.credit_prefix.config(text=MADE[self.lang] + " ")
        self.credit.config(text=AUTHOR)
        self.status.config(text=self.tr("ready"))
        self.update_settings()

    def lang_menu(self):
        m = tk.Menu(self, tearoff=0, bg=self.panel2, fg=self.text, activebackground="#317b61")
        for k, v in LANGS.items():
            m.add_command(label=v, command=lambda x=k: self.set_lang(x))
        m.tk_popup(self.lang_btn.winfo_rootx(), self.lang_btn.winfo_rooty() + 35)

    def set_lang(self, x):
        self.lang = x
        self.refresh()

    def choose_json(self):
        p = filedialog.askopenfilename(filetypes=[("JSON", "*.json"), ("All files", "*.*")])
        if p:
            self.json_path = Path(p)
            self.json_var.set(str(self.json_path))
            self.load()
            self.save_session()

    def choose_output(self):
        p = filedialog.askdirectory()
        if p:
            self.out = Path(p)
            self.out_var.set(str(self.out))
            self.save_session()

    def load_session(self):
        try:
            state = json.loads(session_path().read_text(encoding="utf-8"))
        except Exception:
            return
        json_path = state.get("json_path")
        if json_path and Path(json_path).is_file():
            self.json_path = Path(json_path)
            self.json_var.set(str(self.json_path))
            self.load()
        out = state.get("out")
        if out and Path(out).is_dir():
            self.out = Path(out)
            self.out_var.set(str(self.out))
        zoom = state.get("anim_zoom")
        if isinstance(zoom, (int, float)) and zoom in ZOOM_STEPS:
            self.anim_zoom = float(zoom)

    def save_session(self):
        try:
            p = session_path()
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(
                json.dumps(
                    {
                        "json_path": str(self.json_path) if self.json_path else None,
                        "out": str(self.out) if self.out else None,
                        "anim_zoom": self.anim_zoom,
                    }
                ),
                encoding="utf-8",
            )
        except Exception:
            pass

    def size_changed(self, e=None):
        if self.size_var.get() == self.tr("original"):
            self.original_mode = True
            self.size = None
        else:
            self.original_mode = False
            self.size = int(self.size_var.get().split("x")[0])
        self.update_settings()

    def custom_size(self):
        d = tk.Toplevel(self)
        d.title(self.tr("custom_title"))
        d.configure(bg=self.panel)
        d.resizable(False, False)
        tk.Label(d, text=self.tr("custom_prompt"), bg=self.panel, fg=self.text).pack(
            padx=18, pady=12
        )
        e = tk.Entry(d, bg=self.panel2, fg=self.text, relief="flat")
        e.insert(0, str(self.size) if self.size else "")
        e.pack(padx=18)
        e.focus_set()

        def ok():
            try:
                n = int(e.get())
                assert n > 0
            except Exception:
                messagebox.showerror("Error", self.tr("invalid"), parent=d)
                return
            self.size = n
            self.original_mode = False
            self.size_var.set(f"{n} x {n}")
            d.destroy()
            self.update_settings()

        ttk.Button(d, text="OK", style="Cut.TButton", command=ok).pack(pady=12)
        d.bind("<Return>", lambda e: ok())

    def load(self):
        if not self.json_path:
            return
        try:
            data = json.loads(self.json_path.read_text(encoding="utf-8-sig"))
            png = self.json_path.parent / data["meta"]["image"]
            sheet = Image.open(png).convert("RGBA")
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)
            return
        self.data = data
        self.png = png
        self.png_var.set(str(self.png))
        self.sheet = sheet
        self.render()

    def render(self):
        for w in self.inner.winfo_children():
            w.destroy()
        self.thumbs = []
        frames = self.data.get("frames", {})
        self.count.config(text=f"{len(frames)} sprites")
        groups = {}
        for key, fd in frames.items():
            folder = str(Path(key).parent)
            groups.setdefault(folder, []).append((key, fd))
        cols = 5
        row = 0
        for folder, items in groups.items():
            label = folder if folder != "." else self.tr("root_group")
            head = tk.Frame(self.inner, bg="#0b1016")
            head.grid(
                row=row, column=0, columnspan=cols, sticky="w", padx=4, pady=(14 if row else 0, 6)
            )
            tk.Label(
                head,
                text=f"{label}  ({len(items)})",
                bg="#0b1016",
                fg=self.text,
                font=("Segoe UI", 10, "bold"),
                anchor="w",
            ).pack(side="left")
            ttk.Button(
                head,
                text=self.tr("play_anim"),
                style="Dark.TButton",
                cursor="hand2",
                command=lambda f=folder, it=items: self.play_animation(f, it),
            ).pack(side="left", padx=(10, 0))
            row += 1
            for i, (key, fd) in enumerate(items):
                r, c = row + i // cols, i % cols
                card = tk.Frame(
                    self.inner,
                    bg=self.panel,
                    highlightbackground=self.border,
                    highlightthickness=1,
                )
                card.grid(row=r, column=c, padx=5, pady=5, sticky="n")
                f = fd["frame"]
                im = self.sheet.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))
                im = untrim_frame(im, fd)
                scale = min(110 / max(im.width, im.height), 1)
                im = im.resize(
                    (max(1, int(im.width * scale)), max(1, int(im.height * scale))),
                    Image.Resampling.NEAREST,
                )
                bg = Image.new("RGBA", (116, 116), (38, 45, 56, 255))
                bg.alpha_composite(im, ((116 - im.width) // 2, (116 - im.height) // 2))
                tkim = ImageTk.PhotoImage(bg)
                self.thumbs.append(tkim)
                tk.Button(
                    card,
                    image=tkim,
                    bg=self.panel,
                    activebackground=self.panel,
                    relief="flat",
                    bd=0,
                    command=lambda k=key: self.select(k),
                ).pack(padx=4, pady=4)
                tk.Label(
                    card,
                    text=Path(key).name,
                    bg=self.panel,
                    fg=self.text,
                    font=("Segoe UI", 7),
                    wraplength=110,
                ).pack(pady=(0, 1))
                tk.Label(
                    card,
                    text=f'{f.get("w", "?")} × {f.get("h", "?")}',
                    bg=self.panel,
                    fg=self.muted,
                    font=("Segoe UI", 7),
                ).pack(pady=(0, 4))
            row += -(-len(items) // cols)
        self.selected = next(iter(frames), None)
        self.update_settings()
        self._bind_wheel(self.canvas, self.canvas)

    def select(self, k):
        self.selected = k
        self.update_settings()

    def update_settings(self):
        self.settings.configure(state="normal")
        self.settings.delete("1.0", "end")
        if not self.data or not self.selected:
            self.settings.insert("end", self.tr("select_sprite"))
        else:
            f = self.data["frames"][self.selected]
            fr = f.get("frame", {})
            a = f.get("anchor", {})
            ss = f.get("spriteSourceSize", {})
            src = f.get("sourceSize", {})
            lines = [
                f"Sprite: {self.selected}",
                "",
                f'{self.tr("frame")}: x={fr.get("x", "?")}, y={fr.get("y", "?")}, '
                f'w={fr.get("w", "?")}, h={fr.get("h", "?")}',
                f'{self.tr("anchor")}: X={a.get("x", "—")}, Y={a.get("y", "—")}',
                f'{self.tr("sprite_source")}: x={ss.get("x", "?")}, y={ss.get("y", "?")}, '
                f'w={ss.get("w", "?")}, h={ss.get("h", "?")}',
                f'{self.tr("source")}: {src.get("w", "?")} × {src.get("h", "?")}',
                f'{self.tr("rotated")}: {f.get("rotated", False)}',
                f'{self.tr("trimmed")}: {f.get("trimmed", False)}',
                "",
                f"Sprite output: {fr.get('w', '?')} × {fr.get('h', '?')} ({self.tr('original')})"
                if self.original_mode
                else f"Sprite output: {self.size} × {self.size}",
            ]
            self.settings.insert("end", "\n".join(lines))
        self.settings.configure(state="disabled")

    def targets(self):
        frames = self.data["frames"]
        anim = self.data.get("animations")
        out = {}
        if anim:
            for folder, keys in anim.items():
                for key in keys:
                    if key in frames:
                        out[key] = Path(folder) / Path(key).name
        else:
            for key in frames:
                out[key] = Path(key.replace("/", "_").replace("\\", "_"))
        return out

    def cut(self):
        if not self.data:
            return messagebox.showwarning("Aviso", self.tr("errjson"))
        if not self.out:
            return messagebox.showwarning("Aviso", self.tr("errout"))
        self.out.mkdir(parents=True, exist_ok=True)
        icc = self.sheet.info.get("icc_profile")
        dpi = self.sheet.info.get("dpi")
        n = 0
        for key, rel in self.targets().items():
            fd = self.data["frames"][key]
            f = fd["frame"]
            im = self.sheet.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))
            im = untrim_frame(im, fd)
            if not self.original_mode and im.width <= self.size and im.height <= self.size:
                canvas = Image.new("RGBA", (self.size, self.size), (0, 0, 0, 0))
                canvas.paste(im, ((self.size - im.width) // 2, (self.size - im.height) // 2))
                im = canvas
            path = self.out / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            kw = {}
            if icc:
                kw["icc_profile"] = icc
            if dpi:
                kw["dpi"] = dpi
            im.save(path, **kw)
            n += 1
        self.status.config(text=self.tr("done").format(n=n))
        messagebox.showinfo("TextureSplitter", self.tr("done").format(n=n))

    def play_animation(self, folder, items):
        if not items:
            return messagebox.showinfo("TextureSplitter", self.tr("no_frames"))
        ordered = sorted(items, key=lambda kv: natural_key(Path(kv[0]).name))
        frames = []
        for key, fd in ordered:
            f = fd["frame"]
            cropped = self.sheet.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))
            frames.append(untrim_frame(cropped, fd))
        label = folder if folder != "." else self.tr("root_group")
        AnimationWindow(self, label, frames)

    def make_shortcut(self):
        if os.name != "nt":
            return
        try:
            desktop = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"
            desktop.mkdir(exist_ok=True)
            link = desktop / "TextureSplitter.lnk"
            if getattr(sys, "frozen", False):
                # Running as a PyInstaller executable: launch it directly,
                # since __file__ would point into its ephemeral temp extraction dir.
                target = Path(sys.executable).resolve()
                arguments = ""
                workdir = target.parent
            else:
                app = Path(__file__).resolve()
                py = Path(sys.executable).with_name("pythonw.exe")
                target = py if py.exists() else Path(sys.executable)
                arguments = f'"{app}"'
                workdir = app.parent
            ps = (
                f"$ws=New-Object -ComObject WScript.Shell;"
                f"$s=$ws.CreateShortcut('{link}');"
                f"$s.TargetPath='{target}';"
                f"$s.Arguments='{arguments}';"
                f"$s.WorkingDirectory='{workdir}';"
                f"$s.Description='TextureSplitter';"
                f"$s.Save()"
            )
            subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass


ZOOM_STEPS = [0.5, 1, 2, 4, 8, 16]
ZOOM_MAX_CANVAS = 640


class AnimationWindow(tk.Toplevel):
    def __init__(self, app, label, frames):
        super().__init__(app)
        self.app = app
        self.frames = frames
        self.idx = 0
        self.playing = True
        self.fps = tk.IntVar(value=10)
        self.zoom = app.anim_zoom if app.anim_zoom in ZOOM_STEPS else 1.0
        self.job = None
        self.title(f"{app.tr('play_anim').lstrip('▶ ')} - {label}")
        self.configure(bg=app.panel)
        self.resizable(False, False)
        w = max((im.width for im in frames), default=64)
        h = max((im.height for im in frames), default=64)
        self.base_disp_w, self.base_disp_h = max(w, 160), max(h, 160)
        self.disp_w = min(int(self.base_disp_w * self.zoom), ZOOM_MAX_CANVAS)
        self.disp_h = min(int(self.base_disp_h * self.zoom), ZOOM_MAX_CANVAS)
        self.canvas = tk.Canvas(
            self, width=self.disp_w, height=self.disp_h, bg="#0b1016", highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=10)
        ctrl = tk.Frame(self, bg=app.panel)
        ctrl.pack(fill="x", padx=10, pady=(0, 10))
        self.play_btn = ttk.Button(
            ctrl, style="Dark.TButton", cursor="hand2", command=self.toggle_play
        )
        self.play_btn.pack(side="left")
        ttk.Button(
            ctrl, text=app.tr("stop"), style="Dark.TButton", cursor="hand2", command=self.stop
        ).pack(side="left", padx=(6, 0))
        tk.Label(ctrl, text=app.tr("speed"), bg=app.panel, fg=app.text).pack(
            side="left", padx=(14, 4)
        )
        tk.Scale(
            ctrl,
            from_=1,
            to=30,
            orient="horizontal",
            variable=self.fps,
            bg=app.panel,
            fg=app.text,
            troughcolor=app.panel2,
            highlightthickness=0,
            command=self.on_speed,
        ).pack(side="left", fill="x", expand=True)
        tk.Label(ctrl, text=app.tr("zoom"), bg=app.panel, fg=app.text).pack(
            side="left", padx=(14, 4)
        )
        self.zoom_out_btn = ttk.Button(
            ctrl, text="-", style="Dark.TButton", cursor="hand2", width=2, command=self.zoom_out
        )
        self.zoom_out_btn.pack(side="left")
        self.zoom_label = tk.Label(
            ctrl, text=self.format_zoom(), bg=app.panel, fg=app.text, width=4, anchor="center"
        )
        self.zoom_label.pack(side="left", padx=4)
        self.zoom_in_btn = ttk.Button(
            ctrl, text="+", style="Dark.TButton", cursor="hand2", width=2, command=self.zoom_in
        )
        self.zoom_in_btn.pack(side="left")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.update_play_btn()
        self.update_zoom_btns()
        self.show_frame()
        self.schedule()

    def format_zoom(self):
        z = self.zoom
        return f"{z:g}x"

    def apply_zoom(self, zoom):
        self.zoom = zoom
        self.disp_w = min(int(self.base_disp_w * zoom), ZOOM_MAX_CANVAS)
        self.disp_h = min(int(self.base_disp_h * zoom), ZOOM_MAX_CANVAS)
        self.canvas.config(width=self.disp_w, height=self.disp_h)
        self.zoom_label.config(text=self.format_zoom())
        self.update_zoom_btns()
        self.show_frame()
        self.app.anim_zoom = zoom
        self.app.save_session()

    def zoom_in(self):
        larger = [z for z in ZOOM_STEPS if z > self.zoom]
        if larger:
            self.apply_zoom(larger[0])

    def zoom_out(self):
        smaller = [z for z in ZOOM_STEPS if z < self.zoom]
        if smaller:
            self.apply_zoom(smaller[-1])

    def update_zoom_btns(self):
        self.zoom_out_btn.config(
            state="disabled" if self.zoom <= ZOOM_STEPS[0] else "normal"
        )
        self.zoom_in_btn.config(
            state="disabled" if self.zoom >= ZOOM_STEPS[-1] else "normal"
        )

    def show_frame(self):
        im = self.frames[self.idx]
        if self.zoom != 1.0:
            im = im.resize(
                (max(1, int(im.width * self.zoom)), max(1, int(im.height * self.zoom))),
                Image.NEAREST,
            )
        bg = Image.new("RGBA", (self.disp_w, self.disp_h), (11, 16, 22, 255))
        x = (self.disp_w - im.width) // 2
        y = (self.disp_h - im.height) // 2
        if x < 0 or y < 0:
            im = im.crop((-min(x, 0), -min(y, 0), -min(x, 0) + self.disp_w, -min(y, 0) + self.disp_h))
            x, y = max(x, 0), max(y, 0)
        bg.alpha_composite(im, (x, y))
        self.photo = ImageTk.PhotoImage(bg)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)

    def schedule(self):
        if self.job:
            self.after_cancel(self.job)
            self.job = None
        if self.playing:
            self.job = self.after(int(1000 / max(1, self.fps.get())), self.advance)

    def advance(self):
        self.idx = (self.idx + 1) % len(self.frames)
        self.show_frame()
        self.schedule()

    def toggle_play(self):
        self.playing = not self.playing
        self.update_play_btn()
        self.schedule()

    def stop(self):
        self.playing = False
        self.idx = 0
        self.update_play_btn()
        self.schedule()
        self.show_frame()

    def on_speed(self, _=None):
        self.schedule()

    def update_play_btn(self):
        self.play_btn.config(text=self.app.tr("pause") if self.playing else self.app.tr("play"))

    def close(self):
        if self.job:
            self.after_cancel(self.job)
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
