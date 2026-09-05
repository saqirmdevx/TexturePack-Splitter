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
    QMessageBox,
    QPushButton,
    QSlider,
    QSplitter,
    QStackedWidget,
    QToolBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

import sprite_document
from pack_spritesheet import natural_key
from sprite_document import PIVOT_PRESETS, SpriteDocument

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
                border = QGraphicsRectItem(x - 2, y - 2, disp_w + 4, disp_h + 4)
                border.setPen(QPen(QColor("red"), 2))
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

        self.enable_checkbox = QCheckBox("Enable pivot points")
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

        self.preset_combo = QComboBox()
        self.preset_combo.addItems(list(PIVOT_PRESETS.keys()))
        self.preset_combo.currentTextChanged.connect(self._on_preset_chosen)

        form = QFormLayout()
        form.addRow(self.enable_checkbox)
        form.addRow("Absolute x:", self.abs_x)
        form.addRow("Absolute y:", self.abs_y)
        form.addRow("Normalized x:", self.norm_x)
        form.addRow("Normalized y:", self.norm_y)
        form.addRow("Predefined:", self.preset_combo)
        fields_widget = QWidget()
        fields_widget.setLayout(form)

        placeholder = QLabel("Select a sprite to edit its pivot point.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setWordWrap(True)

        self.stack = QStackedWidget()
        self.stack.addWidget(placeholder)
        self.stack.addWidget(fields_widget)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Settings</b>"))
        layout.addWidget(QLabel("Pivot point"))
        layout.addWidget(self.stack)
        layout.addStretch()

        self._set_fields_enabled(False)

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

    def _on_preset_chosen(self, name):
        if name in PIVOT_PRESETS:
            self._apply_anchor(PIVOT_PRESETS[name])


class PreviewDialog(QDialog):
    def __init__(self, parent, frames):
        super().__init__(parent)
        self.setWindowTitle("Preview Animation")
        self.frames = frames
        self.idx = 0
        self.playing = True

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setMinimumSize(200, 200)

        self.play_btn = QPushButton("Pause")
        self.play_btn.clicked.connect(self._toggle)
        self.speed = QSlider(Qt.Orientation.Horizontal)
        self.speed.setRange(1, 30)
        self.speed.setValue(10)
        self.speed.valueChanged.connect(self._schedule)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        controls = QHBoxLayout()
        controls.addWidget(self.play_btn)
        controls.addWidget(QLabel("Speed:"))
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
        self.label.setPixmap(pil_to_qpixmap(self.frames[self.idx].image))

    def _advance(self):
        self.idx = (self.idx + 1) % len(self.frames)
        self._show_frame()

    def _toggle(self):
        self.playing = not self.playing
        self.play_btn.setText("Pause" if self.playing else "Play")
        self._schedule()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spritesheet Utility (preview)")
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))
        self.doc = None

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

        act_load_sheet = QAction(_render_icon(_icon_picture), "Load Spritesheet", self)
        act_load_sheet.triggered.connect(self._load_spritesheet)
        tb.addAction(act_load_sheet)

        act_load_folder = QAction(_render_icon(_icon_folder), "Load Folder", self)
        act_load_folder.triggered.connect(self._load_folder)
        tb.addAction(act_load_folder)

        tb.addSeparator()

        self.act_split = QAction(_render_icon(_icon_split), "Split Sheet", self)
        self.act_split.triggered.connect(self._do_split)
        self.act_split.setEnabled(False)
        tb.addAction(self.act_split)

        self.act_publish = QAction(_render_icon(_icon_publish), "Publish Sprite Sheet", self)
        self.act_publish.triggered.connect(self._do_publish)
        self.act_publish.setEnabled(False)
        tb.addAction(self.act_publish)

        tb.addSeparator()

        self.act_preview = QAction(_render_icon(_icon_play), "Preview Anims", self)
        self.act_preview.triggered.connect(self._show_preview)
        self.act_preview.setEnabled(False)
        tb.addAction(self.act_preview)

    def _load_spritesheet(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Spritesheet", "", "Spritesheet JSON (*.json)")
        if not path:
            return
        try:
            doc = sprite_document.load_from_spritesheet(Path(path))
        except Exception as e:
            QMessageBox.critical(self, "Load failed", str(e))
            return
        self._set_document(doc)

    def _load_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Load Folder")
        if not path:
            return
        try:
            doc = sprite_document.load_from_folder(Path(path))
        except Exception as e:
            QMessageBox.critical(self, "Load failed", str(e))
            return
        self._set_document(doc)

    def _set_document(self, doc):
        self.doc = doc
        populate_explorer(self.tree, doc)
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
        out = QFileDialog.getExistingDirectory(self, "Split into folder")
        if not out:
            return
        n = sprite_document.export_split(self.doc, Path(out))
        QMessageBox.information(self, "Split Sheet", f"Wrote {n} frame(s) to {out}")

    def _do_publish(self):
        if not self.doc:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Publish Sprite Sheet", f"{self.doc.name}.json", "Spritesheet JSON (*.json)"
        )
        if not path:
            return
        save_path = Path(path)
        png_path, json_path = sprite_document.export_publish(self.doc, save_path.parent, name=save_path.stem)
        QMessageBox.information(
            self, "Publish Sprite Sheet", f"Wrote {png_path.name} + {json_path.name} to {save_path.parent}"
        )

    def _show_preview(self):
        if not self.doc:
            return
        keys = selected_keys(self.tree) or set(self.doc.frames.keys())
        frames = [self.doc.frames[k] for k in sorted(keys, key=sort_key)]
        if not frames:
            return
        PreviewDialog(self, frames).exec()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
