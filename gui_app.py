#!/usr/bin/env python3
"""Spritesheet Utility — new PySide6 GUI (phase 1: layout + pivot-point editing).

Loads either a spritesheet (JSON+PNG) or a folder of frame images into one
in-memory SpriteDocument (see sprite_document.py), lets you multi-select
frames in the Explorer and set a normalized pivot point on them, and exports
either as individual frames (Split Sheet) or as a repacked spritesheet
(Publish Sprite Sheet).

This coexists with the legacy Tkinter GUI (app.py), which is unchanged.
"""

import sys
from contextlib import contextmanager
from pathlib import Path

from PIL import Image, ImageDraw
from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QAction, QBrush, QColor, QIcon, QImage, QPen, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGraphicsEllipseItem,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QToolBar,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

import sprite_document
from pack_spritesheet import natural_key
from sprite_document import PIVOT_PRESETS, SpriteDocument

LANGS = {
    "pt": "🇧🇷 Português",
    "en": "🇺🇸 English",
    "es": "🇪🇸 Español",
    "zh": "🇨🇳 中文",
    "sk": "🇸🇰 Slovenčina",
}

# Positional order matches PIVOT_PRESETS' insertion order (Center, Top left,
# Top center, Bottom center, Bottom right) so combo items can be translated
# by index without disturbing the canonical English keys used as data.
_PRESET_TR_KEYS = ["preset_center", "preset_top_left", "preset_top_center", "preset_bottom_center", "preset_bottom_right"]

T = {
    "en": {
        "load_spritesheet": "Load Spritesheet",
        "load_folder": "Load Folder",
        "split_sheet": "Split Sheet",
        "publish_sheet": "Publish Sprite Sheet",
        "preview_anims": "Preview Anims",
        "settings_title": "Settings",
        "pivot_point": "Pivot point",
        "enable_pivot": "Enable pivot points",
        "absolute_x": "Absolute x:",
        "absolute_y": "Absolute y:",
        "normalized_x": "Normalized x:",
        "normalized_y": "Normalized y:",
        "predefined": "Predefined:",
        "select_sprite": "Select a sprite to edit its pivot point.",
        "frame_size_title": "Frame Size",
        "frame_size_original": "Original",
        "frame_size_custom": "Custom...",
        "preset_center": "Center",
        "preset_top_left": "Top left",
        "preset_top_center": "Top center",
        "preset_bottom_center": "Bottom center",
        "preset_bottom_right": "Bottom right",
        "preview_title": "Preview Animation",
        "play": "Play",
        "pause": "Pause",
        "speed": "Speed:",
        "load_failed_title": "Load failed",
        "split_done_title": "Split Sheet",
        "split_done_msg": "Wrote {n} frame(s) to {out}",
        "publish_done_title": "Publish Sprite Sheet",
        "publish_done_msg": "Wrote {png} + {json} to {out}",
        "dlg_load_spritesheet": "Load Spritesheet",
        "dlg_load_folder": "Load Folder",
        "dlg_split_folder": "Split into folder",
        "dlg_publish": "Publish Sprite Sheet",
        "json_filter": "Spritesheet JSON (*.json)",
    },
    "pt": {
        "load_spritesheet": "Carregar Spritesheet",
        "load_folder": "Carregar Pasta",
        "split_sheet": "Dividir Spritesheet",
        "publish_sheet": "Publicar Spritesheet",
        "preview_anims": "Pré-visualizar Animações",
        "settings_title": "Configurações",
        "pivot_point": "Ponto de pivô",
        "enable_pivot": "Ativar pontos de pivô",
        "absolute_x": "Absoluto x:",
        "absolute_y": "Absoluto y:",
        "normalized_x": "Normalizado x:",
        "normalized_y": "Normalizado y:",
        "predefined": "Predefinido:",
        "select_sprite": "Selecione um sprite para editar seu ponto de pivô.",
        "frame_size_title": "Tamanho do Frame",
        "frame_size_original": "Original",
        "frame_size_custom": "Personalizado...",
        "preset_center": "Centro",
        "preset_top_left": "Superior esquerdo",
        "preset_top_center": "Superior centro",
        "preset_bottom_center": "Inferior centro",
        "preset_bottom_right": "Inferior direito",
        "preview_title": "Pré-visualização da animação",
        "play": "Reproduzir",
        "pause": "Pausar",
        "speed": "Velocidade:",
        "load_failed_title": "Falha ao carregar",
        "split_done_title": "Dividir Spritesheet",
        "split_done_msg": "{n} frame(s) gravado(s) em {out}",
        "publish_done_title": "Publicar Spritesheet",
        "publish_done_msg": "{png} + {json} gravados em {out}",
        "dlg_load_spritesheet": "Carregar Spritesheet",
        "dlg_load_folder": "Carregar Pasta",
        "dlg_split_folder": "Dividir para a pasta",
        "dlg_publish": "Publicar Spritesheet",
        "json_filter": "Spritesheet JSON (*.json)",
    },
    "es": {
        "load_spritesheet": "Cargar Spritesheet",
        "load_folder": "Cargar Carpeta",
        "split_sheet": "Dividir Spritesheet",
        "publish_sheet": "Publicar Spritesheet",
        "preview_anims": "Vista previa de animaciones",
        "settings_title": "Configuración",
        "pivot_point": "Punto de pivote",
        "enable_pivot": "Habilitar puntos de pivote",
        "absolute_x": "Absoluto x:",
        "absolute_y": "Absoluto y:",
        "normalized_x": "Normalizado x:",
        "normalized_y": "Normalizado y:",
        "predefined": "Predefinido:",
        "select_sprite": "Selecciona un sprite para editar su punto de pivote.",
        "frame_size_title": "Tamaño del Frame",
        "frame_size_original": "Original",
        "frame_size_custom": "Personalizado...",
        "preset_center": "Centro",
        "preset_top_left": "Superior izquierda",
        "preset_top_center": "Superior centro",
        "preset_bottom_center": "Inferior centro",
        "preset_bottom_right": "Inferior derecha",
        "preview_title": "Vista previa de animación",
        "play": "Reproducir",
        "pause": "Pausar",
        "speed": "Velocidad:",
        "load_failed_title": "Error al cargar",
        "split_done_title": "Dividir Spritesheet",
        "split_done_msg": "Se guardaron {n} frame(s) en {out}",
        "publish_done_title": "Publicar Spritesheet",
        "publish_done_msg": "Se guardaron {png} + {json} en {out}",
        "dlg_load_spritesheet": "Cargar Spritesheet",
        "dlg_load_folder": "Cargar Carpeta",
        "dlg_split_folder": "Dividir en carpeta",
        "dlg_publish": "Publicar Spritesheet",
        "json_filter": "Spritesheet JSON (*.json)",
    },
    "zh": {
        "load_spritesheet": "加载 Spritesheet",
        "load_folder": "加载文件夹",
        "split_sheet": "拆分 Spritesheet",
        "publish_sheet": "发布 Spritesheet",
        "preview_anims": "预览动画",
        "settings_title": "设置",
        "pivot_point": "锚点",
        "enable_pivot": "启用锚点",
        "absolute_x": "绝对 x：",
        "absolute_y": "绝对 y：",
        "normalized_x": "归一化 x：",
        "normalized_y": "归一化 y：",
        "predefined": "预设：",
        "select_sprite": "选择一个 Sprite 以编辑其锚点。",
        "frame_size_title": "帧大小",
        "frame_size_original": "原始大小",
        "frame_size_custom": "自定义...",
        "preset_center": "居中",
        "preset_top_left": "左上",
        "preset_top_center": "上居中",
        "preset_bottom_center": "下居中",
        "preset_bottom_right": "右下",
        "preview_title": "动画预览",
        "play": "播放",
        "pause": "暂停",
        "speed": "速度：",
        "load_failed_title": "加载失败",
        "split_done_title": "拆分 Spritesheet",
        "split_done_msg": "已写入 {n} 个帧到 {out}",
        "publish_done_title": "发布 Spritesheet",
        "publish_done_msg": "已写入 {png} + {json} 到 {out}",
        "dlg_load_spritesheet": "加载 Spritesheet",
        "dlg_load_folder": "加载文件夹",
        "dlg_split_folder": "拆分到文件夹",
        "dlg_publish": "发布 Spritesheet",
        "json_filter": "Spritesheet JSON (*.json)",
    },
    "sk": {
        "load_spritesheet": "Načítať Spritesheet",
        "load_folder": "Načítať priečinok",
        "split_sheet": "Rozdeliť Spritesheet",
        "publish_sheet": "Publikovať Spritesheet",
        "preview_anims": "Náhľad animácií",
        "settings_title": "Nastavenia",
        "pivot_point": "Bod otáčania",
        "enable_pivot": "Povoliť body otáčania",
        "absolute_x": "Absolútne x:",
        "absolute_y": "Absolútne y:",
        "normalized_x": "Normalizované x:",
        "normalized_y": "Normalizované y:",
        "predefined": "Predvolené:",
        "select_sprite": "Vyberte sprite na úpravu jeho bodu otáčania.",
        "frame_size_title": "Veľkosť frame",
        "frame_size_original": "Pôvodná veľkosť",
        "frame_size_custom": "Vlastné...",
        "preset_center": "Stred",
        "preset_top_left": "Vľavo hore",
        "preset_top_center": "Hore v strede",
        "preset_bottom_center": "Dole v strede",
        "preset_bottom_right": "Vpravo dole",
        "preview_title": "Náhľad animácie",
        "play": "Prehrať",
        "pause": "Pauza",
        "speed": "Rýchlosť:",
        "load_failed_title": "Načítanie zlyhalo",
        "split_done_title": "Rozdeliť Spritesheet",
        "split_done_msg": "Zapísaných {n} snímok do {out}",
        "publish_done_title": "Publikovať Spritesheet",
        "publish_done_msg": "Zapísané {png} + {json} do {out}",
        "dlg_load_spritesheet": "Načítať Spritesheet",
        "dlg_load_folder": "Načítať priečinok",
        "dlg_split_folder": "Rozdeliť do priečinka",
        "dlg_publish": "Publikovať Spritesheet",
        "json_filter": "Spritesheet JSON (*.json)",
    },
}


def t(lang: str, key: str) -> str:
    return T.get(lang, T["en"]).get(key, T["en"].get(key, key))

if getattr(sys, "frozen", False):
    ICON_PATH = Path(sys._MEIPASS) / "favicon.png"
else:
    ICON_PATH = Path(__file__).parent / "assets" / "favicon.png"


def pil_to_qpixmap(im: Image.Image) -> QPixmap:
    im = im.convert("RGBA")
    data = im.tobytes("raw", "RGBA")
    qimage = QImage(data, im.width, im.height, im.width * 4, QImage.Format.Format_RGBA8888)
    return QPixmap.fromImage(qimage)


# --- Toolbar icons -----------------------------------------------------
# Drawn with PIL rather than shipping image assets, supersampled for
# anti-aliased edges at small toolbar sizes.

_ICON_COLOR = (215, 215, 215, 255)


def _render_icon(draw_fn, size: int = 32, supersample: int = 4) -> QIcon:
    big = size * supersample
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(img), big)
    img = img.resize((size, size), Image.LANCZOS)
    return QIcon(pil_to_qpixmap(img))


def _icon_picture(draw, s):
    m = s * 0.14
    lw = max(2, round(s * 0.05))
    draw.rounded_rectangle([m, m, s - m, s - m], radius=s * 0.08, outline=_ICON_COLOR, width=lw)
    r = s * 0.09
    cx, cy = m + s * 0.24, m + s * 0.24
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=_ICON_COLOR, width=lw)
    draw.line(
        [
            (m + s * 0.10, s - m - s * 0.12),
            (m + s * 0.36, s - m - s * 0.40),
            (m + s * 0.56, s - m - s * 0.20),
            (m + s * 0.72, s - m - s * 0.46),
            (s - m - s * 0.06, s - m - s * 0.12),
        ],
        fill=_ICON_COLOR,
        width=lw,
        joint="curve",
    )


def _icon_folder(draw, s):
    lw = max(2, round(s * 0.055))
    m = s * 0.14
    top = m + s * 0.10
    tab_w = s * 0.32
    points = [
        (m, top), (m, s - m), (s - m, s - m), (s - m, top + s * 0.06),
        (m + tab_w + s * 0.10, top + s * 0.06), (m + tab_w, m), (m, m), (m, top),
    ]
    draw.line(points, fill=_ICON_COLOR, width=lw, joint="curve")


def _icon_split(draw, s):
    m = s * 0.16
    gap = s * 0.12
    cell = (s - 2 * m - gap) / 2
    radius = cell * 0.18
    for row in range(2):
        for col in range(2):
            x0 = m + col * (cell + gap)
            y0 = m + row * (cell + gap)
            draw.rounded_rectangle([x0, y0, x0 + cell, y0 + cell], radius=radius, fill=_ICON_COLOR)


def _icon_publish(draw, s):
    lw = max(2, round(s * 0.07))
    cx = s / 2
    top = s * 0.14
    stem_bottom = s * 0.62
    head_w = s * 0.20
    draw.line([(cx, top + head_w * 0.6), (cx, stem_bottom)], fill=_ICON_COLOR, width=lw)
    draw.polygon(
        [(cx - head_w, top + head_w), (cx + head_w, top + head_w), (cx, top)],
        fill=_ICON_COLOR,
    )
    tray_y = s * 0.82
    draw.line([(s * 0.18, tray_y), (s * 0.82, tray_y)], fill=_ICON_COLOR, width=lw)
    draw.line([(s * 0.18, tray_y), (s * 0.18, tray_y - s * 0.14)], fill=_ICON_COLOR, width=lw)
    draw.line([(s * 0.82, tray_y), (s * 0.82, tray_y - s * 0.14)], fill=_ICON_COLOR, width=lw)


def _icon_play(draw, s):
    lw = max(2, round(s * 0.06))
    m = s * 0.12
    draw.ellipse([m, m, s - m, s - m], outline=_ICON_COLOR, width=lw)
    draw.polygon([(s * 0.40, s * 0.30), (s * 0.40, s * 0.70), (s * 0.72, s * 0.50)], fill=_ICON_COLOR)


def sort_key(key: str):
    return [natural_key(part) for part in key.split("/")]


@contextmanager
def block_signals(*widgets):
    for w in widgets:
        w.blockSignals(True)
    try:
        yield
    finally:
        for w in widgets:
            w.blockSignals(False)


def populate_explorer(tree: QTreeWidget, doc: SpriteDocument) -> None:
    tree.clear()
    root_item = QTreeWidgetItem(tree, ["Sprites"])
    folder_items = {(): root_item}

    def get_folder(parts):
        if parts in folder_items:
            return folder_items[parts]
        parent = get_folder(parts[:-1])
        item = QTreeWidgetItem(parent, [parts[-1]])
        folder_items[parts] = item
        return item

    for key in sorted(doc.frames.keys(), key=sort_key):
        parts = tuple(key.split("/"))
        parent = get_folder(parts[:-1])
        leaf = QTreeWidgetItem(parent, [parts[-1]])
        leaf.setData(0, Qt.ItemDataRole.UserRole, key)

    tree.expandAll()


def collect_keys(item: QTreeWidgetItem) -> set:
    key = item.data(0, Qt.ItemDataRole.UserRole)
    if key is not None:
        return {key}
    keys = set()
    for i in range(item.childCount()):
        keys |= collect_keys(item.child(i))
    return keys


def selected_keys(tree: QTreeWidget) -> set:
    keys = set()
    for item in tree.selectedItems():
        keys |= collect_keys(item)
    return keys


class Canvas:
    """Grid of frame thumbnails on a gray, wheel-scrollable/zoomable scene."""

    CELL = 96

    def __init__(self):
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QColor(74, 74, 74))
        self.view = _CanvasView(self.scene)

    def set_frames(self, doc: SpriteDocument, keys_to_show, selected):
        self.scene.clear()
        if not doc:
            return
        cols = max(1, int(self.view.viewport().width() // self.CELL) or 8)
        for i, key in enumerate(sorted(keys_to_show, key=sort_key)):
            frame = doc.frames.get(key)
            if frame is None:
                continue
            pixmap = pil_to_qpixmap(frame.image)
            scale = min((self.CELL - 8) / max(pixmap.width(), 1), (self.CELL - 8) / max(pixmap.height(), 1), 1.0)
            row, col = divmod(i, cols)
            cell_x, cell_y = col * self.CELL, row * self.CELL
            disp_w, disp_h = pixmap.width() * scale, pixmap.height() * scale
            x = cell_x + (self.CELL - disp_w) / 2
            y = cell_y + (self.CELL - disp_h) / 2

            if key in selected:
                border = QGraphicsRectItem(x - 1, y - 1, disp_w + 2, disp_h + 2)
                border.setPen(QPen(QColor(46, 204, 113), 1))
                self.scene.addItem(border)

            item = QGraphicsPixmapItem(pixmap)
            item.setScale(scale)
            item.setPos(x, y)
            self.scene.addItem(item)

            ax, ay = frame.anchor
            dot_x, dot_y = x + ax * disp_w, y + ay * disp_h
            dot = QGraphicsEllipseItem(dot_x - 3, dot_y - 3, 6, 6)
            dot.setBrush(QBrush(QColor("red")))
            dot.setPen(QPen(Qt.PenStyle.NoPen))
            self.scene.addItem(dot)

        rect = self.scene.itemsBoundingRect()
        self.scene.setSceneRect(rect.adjusted(-20, -20, 20, 20))


class _CanvasView(QGraphicsView):
    """Wheel scrolls like a normal canvas; Alt/Option+wheel zooms."""

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            self.scale(factor, factor)
        else:
            super().wheelEvent(event)


class PivotPanel(QWidget):
    """Right-side Settings panel: pivot point editing for the current selection."""

    def __init__(self, on_change):
        super().__init__()
        self._on_change = on_change
        self._doc = None
        self._keys = []
        self.lang = "en"

        self.enable_checkbox = QCheckBox()
        self.enable_checkbox.stateChanged.connect(self._on_enable_toggled)

        self.abs_x = QDoubleSpinBox()
        self.abs_y = QDoubleSpinBox()
        for box in (self.abs_x, self.abs_y):
            box.setRange(0, 100000)
            box.setDecimals(2)
            box.valueChanged.connect(self._on_absolute_changed)

        self.norm_x = QDoubleSpinBox()
        self.norm_y = QDoubleSpinBox()
        for box in (self.norm_x, self.norm_y):
            box.setRange(0.0, 1.0)
            box.setDecimals(5)
            box.setSingleStep(0.01)
            box.valueChanged.connect(self._on_normalized_changed)

        # itemData holds the canonical (untranslated) preset key so selection
        # logic never depends on the currently displayed language.
        self.preset_combo = QComboBox()
        for key in PIVOT_PRESETS:
            self.preset_combo.addItem(key, key)
        self.preset_combo.currentIndexChanged.connect(self._on_preset_chosen)

        self.lbl_absolute_x = QLabel()
        self.lbl_absolute_y = QLabel()
        self.lbl_normalized_x = QLabel()
        self.lbl_normalized_y = QLabel()
        self.lbl_predefined = QLabel()

        form = QFormLayout()
        form.addRow(self.enable_checkbox)
        form.addRow(self.lbl_absolute_x, self.abs_x)
        form.addRow(self.lbl_absolute_y, self.abs_y)
        form.addRow(self.lbl_normalized_x, self.norm_x)
        form.addRow(self.lbl_normalized_y, self.norm_y)
        form.addRow(self.lbl_predefined, self.preset_combo)
        fields_widget = QWidget()
        fields_widget.setLayout(form)

        self.lbl_placeholder = QLabel()
        self.lbl_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_placeholder.setWordWrap(True)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.lbl_placeholder)
        self.stack.addWidget(fields_widget)

        # Frame Size: export-time padding, only meaningful for a document
        # loaded from a spritesheet (not a raw folder of frames) — visibility
        # toggled per-document in set_document().
        self.lbl_frame_size_title = QLabel()
        self.frame_size_combo = QComboBox()
        self.frame_size_combo.addItem("", 0)  # "Original", text set in set_language()
        for size in (16, 32, 64, 128):
            self.frame_size_combo.addItem(f"{size} x {size}", size)
        self.frame_size_combo.addItem("", -1)  # "Custom...", text set in set_language()
        self.frame_size_combo.currentIndexChanged.connect(self._on_frame_size_changed)
        self.frame_size_custom = QSpinBox()
        self.frame_size_custom.setRange(1, 8192)
        self.frame_size_custom.setValue(64)
        self.frame_size_custom.setVisible(False)
        self.frame_size_custom.valueChanged.connect(self._on_frame_size_changed)

        fs_layout = QVBoxLayout()
        fs_layout.setContentsMargins(0, 0, 0, 0)
        fs_layout.addWidget(self.lbl_frame_size_title)
        fs_layout.addWidget(self.frame_size_combo)
        fs_layout.addWidget(self.frame_size_custom)
        self.frame_size_group = QWidget()
        self.frame_size_group.setLayout(fs_layout)
        self.frame_size_group.setVisible(False)

        self.lbl_settings_title = QLabel()
        self.lbl_pivot_point_title = QLabel()

        layout = QVBoxLayout(self)
        layout.addWidget(self.lbl_settings_title)
        layout.addWidget(self.frame_size_group)
        layout.addWidget(self.lbl_pivot_point_title)
        layout.addWidget(self.stack)
        layout.addStretch()

        self._set_fields_enabled(False)
        self.set_language(self.lang)

    def set_document(self, doc: SpriteDocument):
        """Called once per loaded document (not per selection change): resets
        and shows/hides the Frame Size control based on where it came from."""
        show_frame_size = doc is not None and doc.source_kind == "spritesheet"
        if doc is not None:
            doc.frame_size = None
        with block_signals(self.frame_size_combo, self.frame_size_custom):
            self.frame_size_combo.setCurrentIndex(0)
            self.frame_size_custom.setVisible(False)
            self.frame_size_custom.setValue(64)
        self.frame_size_group.setVisible(show_frame_size)

    def set_language(self, lang: str):
        self.lang = lang
        self.lbl_settings_title.setText(f"<b>{t(lang, 'settings_title')}</b>")
        self.lbl_pivot_point_title.setText(t(lang, "pivot_point"))
        self.enable_checkbox.setText(t(lang, "enable_pivot"))
        self.lbl_absolute_x.setText(t(lang, "absolute_x"))
        self.lbl_absolute_y.setText(t(lang, "absolute_y"))
        self.lbl_normalized_x.setText(t(lang, "normalized_x"))
        self.lbl_normalized_y.setText(t(lang, "normalized_y"))
        self.lbl_predefined.setText(t(lang, "predefined"))
        self.lbl_placeholder.setText(t(lang, "select_sprite"))
        for i, tr_key in enumerate(_PRESET_TR_KEYS):
            self.preset_combo.setItemText(i, t(lang, tr_key))
        self.lbl_frame_size_title.setText(t(lang, "frame_size_title"))
        self.frame_size_combo.setItemText(0, t(lang, "frame_size_original"))
        self.frame_size_combo.setItemText(self.frame_size_combo.count() - 1, t(lang, "frame_size_custom"))

    def set_selection(self, doc: SpriteDocument, keys):
        self._doc = doc
        self._keys = list(keys)
        self.stack.setCurrentIndex(1 if self._keys else 0)
        if not self._keys or doc is None:
            return

        first = doc.frames[self._keys[0]]
        with block_signals(self.norm_x, self.norm_y, self.abs_x, self.abs_y, self.enable_checkbox):
            self.enable_checkbox.setChecked(doc.pivot_points_enabled)
            self.norm_x.setValue(first.anchor[0])
            self.norm_y.setValue(first.anchor[1])
            self.abs_x.setValue(first.anchor[0] * first.image.width)
            self.abs_y.setValue(first.anchor[1] * first.image.height)
        self._set_fields_enabled(doc.pivot_points_enabled)

    def _set_fields_enabled(self, enabled: bool):
        for w in (self.abs_x, self.abs_y, self.norm_x, self.norm_y, self.preset_combo):
            w.setEnabled(enabled)

    def _on_enable_toggled(self):
        if self._doc is None:
            return
        self._doc.pivot_points_enabled = self.enable_checkbox.isChecked()
        self._set_fields_enabled(self._doc.pivot_points_enabled)
        self._on_change()

    def _apply_anchor(self, anchor):
        if self._doc is None or not self._keys:
            return
        sprite_document.set_anchor(self._doc, self._keys, anchor)
        first = self._doc.frames[self._keys[0]]
        with block_signals(self.norm_x, self.norm_y, self.abs_x, self.abs_y):
            self.norm_x.setValue(anchor[0])
            self.norm_y.setValue(anchor[1])
            self.abs_x.setValue(anchor[0] * first.image.width)
            self.abs_y.setValue(anchor[1] * first.image.height)
        self._on_change()

    def _on_normalized_changed(self):
        self._apply_anchor((self.norm_x.value(), self.norm_y.value()))

    def _on_absolute_changed(self):
        if self._doc is None or not self._keys:
            return
        first = self._doc.frames[self._keys[0]]
        nx = self.abs_x.value() / first.image.width if first.image.width else 0.0
        ny = self.abs_y.value() / first.image.height if first.image.height else 0.0
        self._apply_anchor((nx, ny))

    def _on_preset_chosen(self, index):
        key = self.preset_combo.itemData(index)
        if key in PIVOT_PRESETS:
            self._apply_anchor(PIVOT_PRESETS[key])

    def _on_frame_size_changed(self, *_):
        if self._doc is None:
            return
        data = self.frame_size_combo.currentData()
        is_custom = data == -1
        self.frame_size_custom.setVisible(is_custom)
        if data == 0:
            self._doc.frame_size = None
        elif is_custom:
            self._doc.frame_size = self.frame_size_custom.value()
        else:
            self._doc.frame_size = data


class PreviewDialog(QDialog):
    def __init__(self, parent, frames, lang="en"):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(t(lang, "preview_title"))
        self.frames = frames
        self.idx = 0
        self.playing = True
        self.zoom = 1.0

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setMinimumSize(200, 200)

        self.play_btn = QPushButton(t(lang, "pause"))
        self.play_btn.clicked.connect(self._toggle)
        self.speed = QSlider(Qt.Orientation.Horizontal)
        self.speed.setRange(1, 30)
        self.speed.setValue(10)
        self.speed.valueChanged.connect(self._schedule)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        controls = QHBoxLayout()
        controls.addWidget(self.play_btn)
        controls.addWidget(QLabel(t(lang, "speed")))
        controls.addWidget(self.speed)
        layout.addLayout(controls)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._advance)
        self._show_frame()
        self._schedule()

    def _schedule(self):
        self.timer.stop()
        if self.playing:
            self.timer.start(int(1000 / self.speed.value()))

    def _show_frame(self):
        pixmap = pil_to_qpixmap(self.frames[self.idx].image)
        if self.zoom != 1.0:
            pixmap = pixmap.scaled(
                max(1, round(pixmap.width() * self.zoom)),
                max(1, round(pixmap.height() * self.zoom)),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )
        self.label.setPixmap(pixmap)

    def _advance(self):
        self.idx = (self.idx + 1) % len(self.frames)
        self._show_frame()

    def _toggle(self):
        self.playing = not self.playing
        self.play_btn.setText(t(self.lang, "pause") if self.playing else t(self.lang, "play"))
        self._schedule()

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            self.zoom = max(0.25, min(16.0, self.zoom * factor))
            self._show_frame()
        else:
            super().wheelEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spritesheet Utility (preview)")
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))
        self.doc = None
        self.lang = "en"

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)

        self.canvas = Canvas()
        self.pivot_panel = PivotPanel(on_change=self._on_selection_changed)

        self._splitter = QSplitter()
        self._splitter.addWidget(self.tree)
        self._splitter.addWidget(self.canvas.view)
        self._splitter.addWidget(self.pivot_panel)
        # Explorer : Canvas : Settings = 1 : 4 : 1, so the canvas gets ~65-66%
        # of the width by default and keeps that ratio as the window resizes.
        self._splitter.setStretchFactor(0, 1)
        self._splitter.setStretchFactor(1, 4)
        self._splitter.setStretchFactor(2, 1)
        self.setCentralWidget(self._splitter)
        self._initial_sizes_applied = False

        self._build_toolbar()
        self.resize(1280, 800)

    def showEvent(self, event):
        super().showEvent(event)
        # Widget geometry only becomes real once shown, so the 1:4:1 default
        # split is applied here (once) rather than in __init__, where
        # setSizes() would be normalized against a not-yet-realized width.
        if not self._initial_sizes_applied:
            self._initial_sizes_applied = True
            total = self._splitter.width()
            self._splitter.setSizes([round(total / 6), round(total * 4 / 6), round(total / 6)])

    def _build_toolbar(self):
        tb = QToolBar("Main")
        tb.setMovable(False)
        tb.setIconSize(QSize(32, 32))
        tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        tb.setStyleSheet("QToolButton { padding: 8px 12px; } QToolBar { spacing: 6px; padding: 4px; }")
        self.addToolBar(tb)

        self.act_load_sheet = QAction(_render_icon(_icon_picture), "", self)
        self.act_load_sheet.triggered.connect(self._load_spritesheet)
        tb.addAction(self.act_load_sheet)

        self.act_load_folder = QAction(_render_icon(_icon_folder), "", self)
        self.act_load_folder.triggered.connect(self._load_folder)
        tb.addAction(self.act_load_folder)

        tb.addSeparator()

        self.act_split = QAction(_render_icon(_icon_split), "", self)
        self.act_split.triggered.connect(self._do_split)
        self.act_split.setEnabled(False)
        tb.addAction(self.act_split)

        self.act_publish = QAction(_render_icon(_icon_publish), "", self)
        self.act_publish.triggered.connect(self._do_publish)
        self.act_publish.setEnabled(False)
        tb.addAction(self.act_publish)

        tb.addSeparator()

        self.act_preview = QAction(_render_icon(_icon_play), "", self)
        self.act_preview.triggered.connect(self._show_preview)
        self.act_preview.setEnabled(False)
        tb.addAction(self.act_preview)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tb.addWidget(spacer)

        self.lang_button = QToolButton()
        self.lang_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        lang_menu = QMenu(self.lang_button)
        for code, label in LANGS.items():
            action = lang_menu.addAction(label)
            action.triggered.connect(lambda checked=False, c=code: self._set_language(c))
        self.lang_button.setMenu(lang_menu)
        tb.addWidget(self.lang_button)

        self._retranslate()

    def _set_language(self, lang: str):
        self.lang = lang
        self._retranslate()

    def _retranslate(self):
        lang = self.lang
        self.act_load_sheet.setText(t(lang, "load_spritesheet"))
        self.act_load_folder.setText(t(lang, "load_folder"))
        self.act_split.setText(t(lang, "split_sheet"))
        self.act_publish.setText(t(lang, "publish_sheet"))
        self.act_preview.setText(t(lang, "preview_anims"))
        self.lang_button.setText("🌐 " + LANGS[lang])
        self.pivot_panel.set_language(lang)

    def _load_spritesheet(self):
        path, _ = QFileDialog.getOpenFileName(
            self, t(self.lang, "dlg_load_spritesheet"), "", t(self.lang, "json_filter")
        )
        if not path:
            return
        try:
            doc = sprite_document.load_from_spritesheet(Path(path))
        except Exception as e:
            QMessageBox.critical(self, t(self.lang, "load_failed_title"), str(e))
            return
        self._set_document(doc)

    def _load_folder(self):
        path = QFileDialog.getExistingDirectory(self, t(self.lang, "dlg_load_folder"))
        if not path:
            return
        try:
            doc = sprite_document.load_from_folder(Path(path))
        except Exception as e:
            QMessageBox.critical(self, t(self.lang, "load_failed_title"), str(e))
            return
        self._set_document(doc)

    def _set_document(self, doc):
        self.doc = doc
        populate_explorer(self.tree, doc)
        self.pivot_panel.set_document(doc)
        self.act_split.setEnabled(True)
        self.act_publish.setEnabled(True)
        self.act_preview.setEnabled(True)
        self._on_selection_changed()

    def _on_selection_changed(self):
        keys = selected_keys(self.tree) if self.doc else set()
        show_keys = keys if keys else (set(self.doc.frames.keys()) if self.doc else set())
        self.canvas.set_frames(self.doc, show_keys, keys)
        self.pivot_panel.set_selection(self.doc, sorted(keys, key=sort_key))

    def _do_split(self):
        if not self.doc:
            return
        out = QFileDialog.getExistingDirectory(self, t(self.lang, "dlg_split_folder"))
        if not out:
            return
        n = sprite_document.export_split(self.doc, Path(out))
        QMessageBox.information(
            self, t(self.lang, "split_done_title"), t(self.lang, "split_done_msg").format(n=n, out=out)
        )

    def _do_publish(self):
        if not self.doc:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, t(self.lang, "dlg_publish"), f"{self.doc.name}.json", t(self.lang, "json_filter")
        )
        if not path:
            return
        save_path = Path(path)
        png_path, json_path = sprite_document.export_publish(self.doc, save_path.parent, name=save_path.stem)
        QMessageBox.information(
            self,
            t(self.lang, "publish_done_title"),
            t(self.lang, "publish_done_msg").format(png=png_path.name, json=json_path.name, out=save_path.parent),
        )

    def _show_preview(self):
        if not self.doc:
            return
        keys = selected_keys(self.tree) or set(self.doc.frames.keys())
        frames = [self.doc.frames[k] for k in sorted(keys, key=sort_key)]
        if not frames:
            return
        PreviewDialog(self, frames, lang=self.lang).exec()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
