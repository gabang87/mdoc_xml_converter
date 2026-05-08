from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QFileDialog, QFrame, QSlider
)
from PySide6.QtGui import QPainter, QPen, QColor, QFont
import math
import sys

# ---------------- CALCULATION ----------------
def calculate_box(max_d, ps):
    box = (max_d * 2.15) / ps
    return int(math.ceil(box / 8) * 8) #round up number


# ---------------- VISUALIZER ----------------
class BoxVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.box_size = None
        self.particle_diameter = None
        self.max_diameter = None

    def update_values(self, box_size, particle_diameter, max_diameter=None):
        self.box_size = box_size
        self.particle_diameter = particle_diameter
        self.max_diameter = max_diameter
        self.update()

    def paintEvent(self, event):
        if not self.box_size or not self.particle_diameter:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # --- scale ---
        available_w = w - 100
        available_h = h - 60
        scale = min(available_w, available_h) / self.box_size * 0.9

        box_px = self.box_size * scale
        particle_px = self.particle_diameter * scale

        cx = w / 2
        cy = h / 2

        # =========================
        # DRAW BOX
        # =========================
        pen_box = QPen(QColor("#F9F21A"), 4)
        painter.setPen(pen_box)
        painter.drawRect(
            cx - box_px / 2,
            cy - box_px / 2,
            box_px,
            box_px
        )

        # =========================
        # DRAW PARTICLE
        # =========================
        pen_particle = QPen(QColor("#00C2A8"), 2, Qt.DashLine)
        painter.setPen(pen_particle)
        painter.drawEllipse(
            cx - particle_px / 2,
            cy - particle_px / 2,
            particle_px,
            particle_px
        )

        # =========================
        # DRAW DIAMETER LINE
        # =========================
        painter.drawLine(
            cx - particle_px / 2,
            cy,
            cx + particle_px / 2,
            cy
        )

        # =========================
        # PARTICLE DIAMETER LABEL (LEFT SIDE)
        # =========================
        painter.setPen(QColor("#00C2A8"))
        label = f" {self.particle_diameter:.1f} Å"
        painter.drawText(
            int(cx - box_px / 2 - 65),
            int(cy + 5),
            label
        )

        # =========================
        # BOX SIZE LABELS
        # =========================
        painter.setPen(QColor("#FFD105"))

        # top - centered
        text_top = f"{int(self.box_size)} px"
        fm = painter.fontMetrics()
        text_width = fm.horizontalAdvance(text_top)
        painter.drawText(
            int(cx - text_width / 2),   # ← centered
            int(cy - box_px / 2 - 10),
            text_top
        )

        # right
        painter.drawText(
            cx + box_px / 2 + 5,
            cy + 5,
            f"{int(self.box_size)} px"
        )

        # =========================
        # MAX DIAMETER INDICATOR
        # =========================
        if self.max_diameter:
            max_px = self.max_diameter * scale

            pen_max = QPen(QColor(QColor(173, 255, 47)), 1, Qt.DotLine)
            painter.setPen(pen_max)
            painter.drawEllipse(
                cx - max_px / 2,
                cy - max_px / 2,
                max_px,
                max_px
            )

            painter.setPen(QColor(127, 255, 0))
            text = f"max: {self.max_diameter:.0f} \u00c5"
            fm = painter.fontMetrics()
            text_width = fm.horizontalAdvance(text)
            painter.drawText(
                int(cx - text_width / 2),
                int(cy + box_px / 2 + 18),
                text
)


# ---------------- SLIDER ROW ----------------
class SliderRow(QWidget):
    """A labeled slider that emits a float value."""

    def __init__(self, label, min_val, max_val, step=1, unit="Å", parent=None):
        super().__init__(parent)
        self.step = step
        self.unit = unit

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label)
        self.label.setFixedWidth(110)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(int(min_val / step))
        self.slider.setMaximum(int(max_val / step))
        self.slider.setValue(int(min_val / step))
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #444;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #00C2A8;
                border: 2px solid #00C2A8;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QSlider::sub-page:horizontal {
                background: #00C2A8;
                border-radius: 3px;
            }
        """)

        self.value_label = QLabel(f"{min_val:.0f} {unit}")
        self.value_label.setFixedWidth(70)
        self.value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.value_label.setStyleSheet("color: #FFFFFF; font-weight: bold;")

        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.value_label)

        self.slider.valueChanged.connect(self._on_change)

    def _on_change(self, v):
        real = v * self.step
        self.value_label.setText(f"{real:.0f} {self.unit}")

    def value(self):
        return self.slider.value() * self.step

    def set_value(self, v):
        self.slider.setValue(int(v / self.step))


# ---------------- APP ----------------
class App(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(200, 200, 1050, 520)
        self.setWindowTitle("Dose Calculator")

        self.setStyleSheet("""
            QWidget {
                background-color: #2a2a2a;
                color: white;
                font-size: 14px;
            }
            QLineEdit {
                background-color: white;
                color: black;
                border: 3px solid #3a3a3a;
                border-radius: 10px;
                padding: 6px;
            }
            QPushButton {
                background-color: #009E86;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #04c9a8;
            }
        """)

        self.last_result_text = ""
        self.last_box_text = ""

        # -------- INPUTS --------
        self.ps = QLineEdit()
        self.ps.setPlaceholderText("Pixel size (Å/pixel)")

        self.dr = QLineEdit()
        self.dr.setPlaceholderText("Dose rate (e/pixel/s)")

        self.et = QLineEdit()
        self.et.setPlaceholderText("Exposure time (s)")

        self.ft = QLineEdit()
        self.ft.setPlaceholderText("Frame time (s)")

        # -------- BUTTONS --------
        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.run)

        self.save_button = QPushButton("Save Parameters")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #FFD105;
                color: black;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        self.save_button.clicked.connect(self.save_results)

        self.box_button = QPushButton("Box Extraction")
        self.box_button.setStyleSheet("""
            QPushButton {
                background-color: #0372AD;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover { background-color: #0096C7; }
            QPushButton:pressed { background-color: #023E8A; }
        """)
        self.box_button.clicked.connect(self.compute_box)

        # -------- PARTICLE INPUT --------
        self.min_d = QLineEdit()
        self.min_d.setPlaceholderText("Min diameter (Å)")

        self.max_d = QLineEdit()
        self.max_d.setPlaceholderText("Max diameter (Å)")

        particle_layout = QVBoxLayout()

        title_pp = QLabel("Particles Extraction")
        title_pp.setAlignment(Qt.AlignCenter)

        row = QHBoxLayout()
        row.addWidget(self.min_d)
        row.addWidget(self.max_d)
        row.addWidget(self.box_button)

        particle_layout.addWidget(title_pp)
        particle_layout.addLayout(row)

        # -------- SLIDER SECTION --------
        slider_title = QLabel("Particles Size Explorer")
        slider_title.setAlignment(Qt.AlignCenter)
        slider_title.setStyleSheet("font-weight: bold; margin-top: 2px; color: #FFFFFF;")

        self.diameter_slider = SliderRow("Diameter", 10, 1000, step=5, unit="Å")
        self.diameter_slider.slider.valueChanged.connect(self._on_slider_change)

        self.box_info_label = QLabel("Box size: —    |    Diameter: —")
        self.box_info_label.setAlignment(Qt.AlignCenter)
        self.box_info_label.setStyleSheet("""
            background-color: #111;
            border: 1px solid #444;
            border-radius: 6px;
            padding: 5px;
            color: #FFD105;
            font-size: 13px;
        """)

        self.box_slider = SliderRow("Box Size", 8, 1000, step=8, unit="px")
        self.box_slider.slider.valueChanged.connect(self._on_slider_change)

        particle_layout.addWidget(slider_title)
        particle_layout.addWidget(self.diameter_slider)
        particle_layout.addWidget(self.box_slider)
        particle_layout.addWidget(self.box_info_label)

        particle_frame = QFrame()
        particle_frame.setLayout(particle_layout)
        particle_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #444;
                border-radius: 10px;
                padding: 10px;
                background-color: #1f1f1f;
            }
        """)

        # -------- VISUALIZER --------
        self.visualizer = BoxVisualizer()
        self.visualizer.setMinimumHeight(160)

        # -------- RESULTS --------
        self.result = QLabel("")
        self.result.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.result.setStyleSheet("""
            background-color: #1f1f1f;
            border: 2px solid #444;
            border-radius: 10px;
            padding: 10px;
        """)

        self.signature = QLabel("© Gabriella Angiulli • 2026")
        self.signature.setAlignment(Qt.AlignCenter)
        self.signature.setStyleSheet("color:#aaa; font-size:10px;")

        # -------- LEFT PANEL --------
        left_widget = QWidget()
        left = QVBoxLayout(left_widget)

        left.addWidget(self.ps)
        left.addWidget(self.dr)
        left.addWidget(self.et)
        left.addWidget(self.ft)
        left.addWidget(self.calculate_button)
        left.addWidget(self.save_button)

        # Legend
        legend_title = QLabel("Legend")
        legend_title.setStyleSheet("font-weight: bold; margin-top: 15px;")

        box_icon = QLabel("   ")
        box_icon.setFixedSize(18, 18)
        box_icon.setStyleSheet("background-color: transparent; border: 2px solid #F9F21A;")
        box_text = QLabel("Box Size")
        box_row = QHBoxLayout()
        box_row.addWidget(box_icon)
        box_row.addWidget(box_text)
        box_row.addStretch()
        box_widget = QWidget()
        box_widget.setLayout(box_row)

        particle_icon = QLabel("   ")
        particle_icon.setFixedSize(18, 18)
        particle_icon.setStyleSheet("background-color: transparent; border: 2px dashed #00C2A8; border-radius: 9px;")
        particle_text = QLabel("Particle Diameter")
        particle_row = QHBoxLayout()
        particle_row.addWidget(particle_icon)
        particle_row.addWidget(particle_text)
        particle_row.addStretch()
        particle_widget_legend = QWidget()
        particle_widget_legend.setLayout(particle_row)

        # Max diameter legend
        max_icon = QLabel("   ")
        max_icon.setFixedSize(18, 18)
        max_icon.setStyleSheet("background-color: transparent; border: 2px dotted rgba(127,255,0,255); border-radius: 9px;")
        max_text = QLabel("Max Diameter")
        max_row = QHBoxLayout()
        max_row.addWidget(max_icon)
        max_row.addWidget(max_text)
        max_row.addStretch()
        max_widget = QWidget()
        max_widget.setLayout(max_row)

        legend_container = QWidget()
        legend_layout = QVBoxLayout(legend_container)
        legend_layout.setContentsMargins(0, 6, 0, 4)
        legend_layout.setSpacing(0)
        legend_layout.addWidget(legend_title)
        legend_layout.addWidget(box_widget)
        legend_layout.addWidget(particle_widget_legend)
        legend_layout.addWidget(max_widget)

        left.addWidget(legend_container)
        left.addStretch()
        left_widget.setFixedWidth(250)

        # -------- RIGHT PANEL --------
        right = QVBoxLayout()
        right.setSpacing(6)

        title = QLabel("")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 15px;")

        # result and particle frame side by side
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        top_row.addWidget(self.result, stretch=1)

        right_col = QVBoxLayout()
        right_col.setSpacing(6)
        right_col.addWidget(particle_frame)
        right_col.addWidget(self.visualizer)

        top_row.addLayout(right_col, stretch=1)

        right.addWidget(title)
        right.addLayout(top_row)
        right.addStretch()
        right.addWidget(self.signature)

        # -------- MAIN --------
        main = QHBoxLayout()
        main.addWidget(left_widget)

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("color:#444; margin-left: 10px; margin-right: 10px;")

        main.addWidget(sep)
        main.addLayout(right)

        self.setLayout(main)

    # ---------------- SLIDER LIVE UPDATE ----------------
    def _on_slider_change(self):
        d = self.diameter_slider.value()
        box_slider_val = self.box_slider.value()

        # Try to get pixel size from field; default to 1.0 if not set
        try:
            ps = float(self.ps.text())
            if ps <= 0:
                raise ValueError
        except (ValueError, AttributeError):
            ps = 1.0

        # Try to get max diameter -- used to fix scale and draw reference circle
        try:
            max_d_val = float(self.max_d.text())
            if max_d_val <= 0:
                raise ValueError
        except (ValueError, AttributeError):
            max_d_val = None

        # Box: use box slider if it has been set (>8), else calculate from max_d
        fixed_d = max_d_val if max_d_val else d
        box_from_formula = calculate_box(fixed_d, ps)
        box = box_slider_val if box_slider_val > 8 else box_from_formula

        # Expand box slider max if needed
        if box_from_formula > self.box_slider.slider.maximum() * self.box_slider.step:
            self.box_slider.slider.setMaximum(int(box_from_formula * 2 / self.box_slider.step))

        self.box_info_label.setText(
            f"Box size: {box} px    |    Diameter: {d:.0f} Å    |    Pixel size: {ps} Å/px"
        )
        self.visualizer.update_values(box, d, max_diameter=max_d_val)

    # ---------------- BOX ----------------
    def compute_box(self):
        try:
            ps = float(self.ps.text())
            max_d = float(self.max_d.text())
            box = calculate_box(max_d, ps)

            self.last_box_text = (
                "----- BOX EXTRACTION -----\n"
                f"Max diameter: {max_d} Å\n"
                f"Pixel size: {ps} Å/pixel\n"
                f"Box size: {box} px\n"
            )

            self.result.setText(self.last_result_text + "\n" + self.last_box_text)

            # Expand diameter slider range to 2x max_d
            slider_max = max(1000, int(max_d * 2))
            self.diameter_slider.slider.setMaximum(int(slider_max / self.diameter_slider.step))
            if 10 <= max_d <= slider_max:
                self.diameter_slider.set_value(max_d)

            # Sync box slider to computed box size
            box_slider_max = max(1000, box * 2)
            self.box_slider.slider.setMaximum(int(box_slider_max / self.box_slider.step))
            self.box_slider.set_value(box)

            self.visualizer.update_values(box, max_d, max_diameter=max_d)

        except Exception as e:
            self.result.setText(f"Error: {e}")

    # ---------------- DOSE ----------------
    def run(self):
        try:
            ps = float(self.ps.text())
            dr = float(self.dr.text())
            et = float(self.et.text())
            ft = float(self.ft.text())

            frames = math.floor(et / ft)
            total_dose = (dr * et) / (ps ** 2)
            dose_per_frame = total_dose / frames if frames else 0

            self.last_result_text = (
                "----- INPUT PARAMETERS -----\n"
                f"Pixel Size: {ps} Å/pixel\n"
                f"Dose Rate: {dr} e/pixel/s\n"
                f"Exposure Time: {et} s\n"
                f"Frame Time: {ft} s\n\n"
                "----- OUTPUT PARAMETERS -----\n"
                f"Frames: {frames}\n"
                f"Total Dose: {total_dose:.2f} e/\u00c5\u00b2\n"
                f"Dose/s: {total_dose/et:.2f} e/\u00c5\u00b2/s\n"
                f"Dose/frame: {dose_per_frame:.2f} e/\u00c5\u00b2/frame\n"
            )

            self.result.setText(self.last_result_text)

            # Refresh visualizer with updated pixel size if already showing
            if self.visualizer.particle_diameter:
                self._on_slider_change()

        except Exception as e:
            self.result.setText(f"Error: {e}")

    # ---------------- SAVE ----------------
    def save_results(self):
        if not self.last_result_text:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "dose_results.txt", "Text Files (*.txt)"
        )

        if file_path:
            with open(file_path, "w") as f:
                f.write(self.result.text())


# ---------------- RUN ----------------
app = QApplication(sys.argv)
window = App()
window.show()
sys.exit(app.exec())
