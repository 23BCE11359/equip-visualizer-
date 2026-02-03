import sys
import requests
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Extra imports to help PyInstaller detect PyQt5/Matplotlib when analyzing
# (kept inside an always-false branch so they are not executed at runtime)
if False:  # pragma: no cover
    import PyQt5.QtGui
    try:
        import PyQt5.sip
    except Exception:
        pass
    import matplotlib.backends.backend_qt5agg  # noqa: F401
    import matplotlib  # noqa: F401

import os
import json
from pathlib import Path

API_BASE = 'http://127.0.0.1:8000/api'
CONFIG_FILENAME = '.chemical_visualizer_config.json'

THEME_CSS = """
QWidget { background-color: #fffaf0; font-family: "Segoe UI", Arial; }
QLabel#header { font-size: 16pt; font-weight: 600; color: #ff6b6b; }
QLabel#subheader { font-size: 9pt; color: #7b6f63; margin-left:8px; }
QPushButton { background-color: #ffb88c; border: none; padding: 6px 10px; border-radius: 6px; color: #3b2f2f; }
QPushButton:hover { background-color: #ff9a5a; }
QTableWidget { background: #ffffff; border: 1px solid #eee; border-radius: 6px; }
QComboBox { padding: 6px; }
QLabel#status { color: #5b5b5b; padding:6px 0; }
"""

ALT_THEME_CSS = """
QWidget { background-color: #f4f7fb; font-family: "Segoe UI", Arial; }
QLabel#header { font-size: 16pt; font-weight: 600; color: #2d6cdf; }
QLabel#subheader { font-size: 9pt; color: #566872; margin-left:8px; }
QPushButton { background-color: #dbeafe; border: none; padding: 6px 10px; border-radius: 6px; color: #0b2545; }
QPushButton:hover { background-color: #bcd6ff; }
QTableWidget { background: #ffffff; border: 1px solid #e6eef9; border-radius: 6px; }
QComboBox { padding: 6px; }
QLabel#status { color: #5b5b5b; padding:6px 0; }
"""

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)

    def plot_bar(self, labels, values, title=''):
        self.axes.clear()
        self.axes.bar(labels, values)
        self.axes.set_title(title)
        self.axes.tick_params(axis='x', rotation=45)
        self.draw()

    def plot_line(self, labels, values, title=''):
        self.axes.clear()
        self.axes.plot(labels, values, marker='o')
        self.axes.set_title(title)
        self.axes.tick_params(axis='x', rotation=45)
        self.draw()


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Chemical Visualizer — Desktop')
        self.resize(900, 700)

        layout = QtWidgets.QVBoxLayout()
        header_layout = QtWidgets.QHBoxLayout()
        brand = QtWidgets.QLabel('Chemical Visualizer')
        brand.setObjectName('header')
        brand.setFont(QtGui.QFont('Segoe UI', 14, QtGui.QFont.Bold))
        sub = QtWidgets.QLabel('Upload CSV · Explore · Reports')
        sub.setObjectName('subheader')
        header_layout.addWidget(brand)
        header_layout.addWidget(sub)
        # Accessibility controls
        header_layout.addStretch()
        self.btn_decrease_font = QtWidgets.QPushButton('A-')
        self.btn_decrease_font.setToolTip('Decrease font size')
        self.btn_decrease_font.setFixedSize(34, 24)
        self.btn_increase_font = QtWidgets.QPushButton('A+')
        self.btn_increase_font.setToolTip('Increase font size')
        self.btn_increase_font.setFixedSize(34, 24)
        self.btn_toggle_theme = QtWidgets.QPushButton('Warm')
        self.btn_toggle_theme.setToolTip('Toggle theme')
        self.btn_toggle_theme.setFixedSize(60, 24)
        header_layout.addWidget(self.btn_decrease_font)
        header_layout.addWidget(self.btn_increase_font)
        header_layout.addWidget(self.btn_toggle_theme)
        layout.addLayout(header_layout)

        self.status_label = QtWidgets.QLabel('Welcome — Ready')
        self.status_label.setObjectName('status')
        self.status_label.setStyleSheet('color: #5b5b5b; padding: 6px 0;')
        layout.addWidget(self.status_label) 

        btn_layout = QtWidgets.QHBoxLayout()
        self.upload_btn = QtWidgets.QPushButton('Upload CSV')
        self.refresh_btn = QtWidgets.QPushButton('Refresh')
        self.report_btn = QtWidgets.QPushButton('Download PDF Report')
        self.set_token_btn = QtWidgets.QPushButton('Set Token')
        btn_layout.addWidget(self.upload_btn)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.report_btn)
        btn_layout.addWidget(self.set_token_btn)
        self.token = None

        layout.addLayout(btn_layout)

        self.dataset_list = QtWidgets.QComboBox()
        layout.addWidget(self.dataset_list)

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Name','Type','Material','Flowrate','Pressure','Temperature'])
        layout.addWidget(self.table)

        charts_layout = QtWidgets.QHBoxLayout()
        self.pressure_canvas = PlotCanvas(self, width=5, height=4)
        self.temp_canvas = PlotCanvas(self, width=5, height=4)
        charts_layout.addWidget(self.pressure_canvas)
        charts_layout.addWidget(self.temp_canvas)

        layout.addLayout(charts_layout)

        self.setLayout(layout)

        # Signals
        self.set_api_btn = QtWidgets.QPushButton('Set API URL')
        btn_layout.addWidget(self.set_api_btn)
        self.set_api_btn.clicked.connect(self.set_api_url)

        self.upload_btn.clicked.connect(self.upload_csv)
        self.refresh_btn.clicked.connect(self.load_datasets)
        self.dataset_list.currentIndexChanged.connect(self.dataset_changed)
        self.report_btn.clicked.connect(self.download_report)
        self.set_token_btn.clicked.connect(self.set_token)

        # Accessibility buttons
        self.btn_increase_font.clicked.connect(lambda: self._change_font_pointsize(1))
        self.btn_decrease_font.clicked.connect(lambda: self._change_font_pointsize(-1))
        self.btn_toggle_theme.clicked.connect(self._toggle_theme)

        # Configuration (persisted between runs)
        self.api_base = API_BASE
        self.config_path = str(Path.home() / CONFIG_FILENAME)
        self.theme = 'warm'  # default
        self.load_config()
        # Apply loaded theme
        try:
            if getattr(self, 'theme', 'warm') == 'neutral':
                self._apply_theme('neutral')
            else:
                self._apply_theme('warm')
        except Exception:
            pass
        # Toast queue and state
        self._toast_queue = []
        self._toast_active = False

        self.datasets = []
        self.load_datasets()

    def load_datasets(self):
        try:
            res = requests.get(f'{self.api_base}/datasets/', timeout=5)
            res.raise_for_status()
            self.datasets = res.json()
            self.dataset_list.clear()
            if self.datasets:
                self.status_label.setText(f'Connected — {len(self.datasets)} datasets available')
            else:
                self.status_label.setText('Connected — no datasets found')
            for ds in self.datasets:
                self.dataset_list.addItem(f"{ds['name']} ({ds['equipment_count']} items)", ds['id'])
            if self.datasets:
                self.dataset_list.setCurrentIndex(0)
            else:
                self.table.setRowCount(0)
        except requests.exceptions.ConnectionError as e:
            # Show actionable dialog allowing retry, set API URL, open docs, or exit
            self.show_connection_error_dialog(e)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load datasets: {e}')

    def dataset_changed(self, idx):
        if idx < 0 or idx >= len(self.datasets):
            return
        dsid = self.datasets[idx]['id']
        try:
            res = requests.get(f'{self.api_base}/equipment/?dataset={dsid}', timeout=5)
            res.raise_for_status()
            data = res.json().get('results', [])
            self.populate_table(data)
            labels = [d['name'] for d in data]
            pressures = [d['pressure'] for d in data]
            temps = [d['temperature'] for d in data]
            self.pressure_canvas.plot_bar(labels, pressures, 'Pressure')
            self.temp_canvas.plot_line(labels, temps, 'Temperature')
            self.status_label.setText(f"Showing dataset: {self.datasets[idx]['name']}")
        except requests.exceptions.ConnectionError as e:
            self.status_label.setText('Disconnected — cannot reach backend')
            self.show_connection_error_dialog(e)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load equipment: {e}')

    def populate_table(self, data):
        self.table.setRowCount(len(data))
        for r, item in enumerate(data):
            self.table.setItem(r, 0, QtWidgets.QTableWidgetItem(str(item.get('name'))))
            self.table.setItem(r, 1, QtWidgets.QTableWidgetItem(str(item.get('type') or '')))
            self.table.setItem(r, 2, QtWidgets.QTableWidgetItem(str(item.get('material') or '')))
            self.table.setItem(r, 3, QtWidgets.QTableWidgetItem(str(item.get('flowrate') or '')))
            self.table.setItem(r, 4, QtWidgets.QTableWidgetItem(str(item.get('pressure') or '')))
            self.table.setItem(r, 5, QtWidgets.QTableWidgetItem(str(item.get('temperature') or '')))

    def upload_csv(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Select CSV', '', 'CSV Files (*.csv)')
        if not fname:
            return
        try:
            with open(fname, 'rb') as f:
                filename = os.path.basename(fname)
                files = {'file': (filename, f, 'text/csv')}
                headers = {}
                if getattr(self, 'token', None):
                    headers['Authorization'] = f'Token {self.token}'
                res = requests.post(f'{self.api_base}/upload/', files=files, headers=headers)
                res.raise_for_status()
                created = res.json().get('created')
                QMessageBox.information(self, 'Success', f"Upload complete — created {created} items.")
                self.load_datasets()
                self.status_label.setText(f'Upload complete — {created} items added')
                try:
                    self.show_toast(f'Upload complete — {created} items')
                except Exception:
                    pass
        except requests.exceptions.ConnectionError as e:
            self.show_connection_error_dialog(e)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Upload failed: {e}')

    def download_report(self):
        idx = self.dataset_list.currentIndex()
        if idx < 0 or idx >= len(self.datasets):
            QMessageBox.information(self, 'Info', 'Please select a dataset first.')
            return
        dsid = self.datasets[idx]['id']
        try:
            headers = {}
            if getattr(self, 'token', None):
                headers['Authorization'] = f'Token {self.token}'
            res = requests.get(f'{self.api_base}/datasets/{dsid}/report/pdf/', stream=True, headers=headers)
            if res.status_code == 501:
                QMessageBox.information(self, 'Info', 'Server does not support PDF generation (reportlab missing).')
                return
            if res.status_code in (401, 403):
                QMessageBox.warning(self, 'Auth', 'Report generation requires authentication. Use "Set Token" to provide a token.')
                return
            res.raise_for_status()
            save_fname, _ = QFileDialog.getSaveFileName(self, 'Save Report', f'dataset_{dsid}.pdf', 'PDF files (*.pdf)')
            if save_fname:
                with open(save_fname, 'wb') as fh:
                    for chunk in res.iter_content(chunk_size=8192):
                        fh.write(chunk)
                QMessageBox.information(self, 'Saved', f'Report saved to {save_fname}')
                self.status_label.setText('Report saved')
                try:
                    self.show_toast('Report saved')
                except Exception:
                    pass
        except requests.exceptions.ConnectionError as e:
            self.status_label.setText('Disconnected — cannot reach backend')
            self.show_connection_error_dialog(e)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Report download failed: {e}')

    def set_token(self):
        token, ok = QtWidgets.QInputDialog.getText(self, 'Set Token', 'Enter API token:')
        if ok and token:
            self.token = token
            try:
                self.save_config()
            except Exception:
                pass
            QMessageBox.information(self, 'Token set', "You're all set — token saved.")
            try:
                self.show_toast("You're all set — token saved.")
            except Exception:
                pass

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as fh:
                    cfg = json.load(fh)
                self.api_base = cfg.get('api_base', self.api_base)
                self.token = cfg.get('token', self.token)
                if 'font_size' in cfg and cfg.get('font_size'):
                    try:
                        f = QtWidgets.QApplication.instance().font()
                        f.setPointSize(int(cfg.get('font_size')))
                        QtWidgets.QApplication.instance().setFont(f)
                    except Exception:
                        pass
                if 'theme' in cfg and cfg.get('theme'):
                    try:
                        self.theme = cfg.get('theme')
                    except Exception:
                        pass
        except Exception as e:
            print('load_config error:', e)

    def save_config(self):
        try:
            font_size = None
            try:
                font_size = QtWidgets.QApplication.instance().font().pointSize()
            except Exception:
                font_size = None
            with open(self.config_path, 'w') as fh:
                json.dump({'api_base': self.api_base, 'token': self.token, 'font_size': font_size, 'theme': getattr(self, 'theme', 'warm')}, fh)
        except Exception as e:
            print('save_config error:', e)

    def announce_for_screenreaders(self, message):
        """Try to make a message discoverable to screen readers by briefly focusing it."""
        try:
            # Create a hidden label and set accessible name
            a = QtWidgets.QLabel('', self)
            a.setAccessibleName(message)
            a.setVisible(False)
            a.setFocusPolicy(QtCore.Qt.NoFocus)
            a.show()
            a.setFocus()
            QtCore.QTimer.singleShot(200, lambda: a.hide())
        except Exception:
            pass

    def show_toast(self, message, timeout=3000):
        """Show a transient compact toast. Supports stacking (up to 3) and dismiss button.
        Also announces text to assistive tech."""
        try:
            # create a container widget for toast
            container = QtWidgets.QWidget(self)
            container.setStyleSheet('background: rgba(11,11,11,0.88); color: white; padding: 6px 10px; border-radius: 8px;')
            h = QtWidgets.QHBoxLayout(container)
            lbl = QtWidgets.QLabel(message, container)
            lbl.setStyleSheet('color: white;')
            btn = QtWidgets.QPushButton('\u2715', container)
            btn.setFixedSize(18, 18)
            btn.setStyleSheet('background: rgba(255,255,255,0.08); color: #fff; border:none; border-radius:9px;')
            btn.setToolTip('Dismiss')
            h.addWidget(lbl)
            h.addStretch()
            h.addWidget(btn)
            container.setLayout(h)
            container.adjustSize()

            # position: stacked from top, offset by existing active toasts
            y_offset = 12 + len(getattr(self, '_active_toasts', [])) * (container.height() + 8)
            x = (self.width() - container.width()) // 2
            container.move(x, y_offset)
            container.show()

            # ensure containers list exists
            if not hasattr(self, '_active_toasts'):
                self._active_toasts = []
            self._active_toasts.append(container)

            def _cleanup():
                try:
                    if container in self._active_toasts:
                        self._active_toasts.remove(container)
                    container.hide()
                    container.deleteLater()
                    # reposition remaining
                    for i, c in enumerate(self._active_toasts):
                        c.move((self.width() - c.width()) // 2, 12 + i * (c.height() + 8))
                except Exception:
                    pass

            btn.clicked.connect(_cleanup)
            QtCore.QTimer.singleShot(timeout, _cleanup)

            # announce for accessibility
            try:
                self.announce_for_screenreaders(message)
            except Exception:
                pass

        except Exception:
            # fallback to old simple label
            try:
                toast = QtWidgets.QLabel(message, self)
                toast.setStyleSheet('background: rgba(11,11,11,0.85); color: white; padding: 8px 12px; border-radius: 8px;')
                toast.adjustSize()
                x = (self.width() - toast.width()) // 2
                toast.move(x, 12)
                toast.show()
                QtCore.QTimer.singleShot(timeout, lambda: toast.hide())
            except Exception:
                pass

    def resizeEvent(self, event):
        # Reposition active toasts when window resizes
        try:
            for i, c in enumerate(getattr(self, '_active_toasts', [])):
                c.move((self.width() - c.width()) // 2, 12 + i * (c.height() + 8))
        except Exception:
            pass
        return super().resizeEvent(event) 

    def set_api_url(self):
        url, ok = QtWidgets.QInputDialog.getText(self, 'Set API URL', 'Enter API base URL (e.g. http://127.0.0.1:8000/api):', text=self.api_base)
        if ok and url:
            self.api_base = url.strip()
            try:
                self.save_config()
            except Exception:
                pass
            self.status_label.setText(f'API URL set to {self.api_base}')
            try:
                self.show_toast('API URL updated')
            except Exception:
                pass
            QMessageBox.information(self, 'Saved', f'API URL set to {self.api_base}')

    def _change_font_pointsize(self, delta):
        try:
            app = QtWidgets.QApplication.instance()
            f = app.font()
            current = f.pointSize()
            new = max(8, current + delta)
            f.setPointSize(new)
            app.setFont(f)
            self.show_toast('Font size updated')
            try:
                self.save_config()
            except Exception:
                pass
        except Exception:
            pass

    def _apply_theme(self, name: str):
        if name == 'neutral' or name == 'neutral':
            QtWidgets.QApplication.instance().setStyleSheet(ALT_THEME_CSS)
            self.btn_toggle_theme.setText('Neutral')
            self.theme = 'neutral'
        else:
            QtWidgets.QApplication.instance().setStyleSheet(THEME_CSS)
            self.btn_toggle_theme.setText('Warm')
            self.theme = 'warm'

    def _toggle_theme(self):
        try:
            self._apply_theme('neutral' if self.theme == 'warm' else 'warm')
            self.save_config()
            self.show_toast('Theme updated')
        except Exception:
            pass

    def show_connection_error_dialog(self, error):
        """Show an actionable dialog when the backend cannot be reached."""
        msg = QMessageBox(self)
        msg.setWindowTitle('Connection Error')
        msg.setText(f"We couldn't reach the backend at {self.api_base}.\n\nError: {error}\n\nMake sure the backend server is running (e.g., python manage.py runserver) and that the API URL is correct. You can Retry or Set API URL to fix the issue.")
        retry = msg.addButton('Retry', QMessageBox.AcceptRole)
        setapi = msg.addButton('Set API URL', QMessageBox.ActionRole)
        open_docs = msg.addButton('Open docs', QMessageBox.HelpRole)
        exit_btn = msg.addButton('Exit', QMessageBox.RejectRole)
        msg.exec_()
        clicked = msg.clickedButton()
        if clicked == retry:
            # Retry loading datasets
            self.load_datasets()
        elif clicked == setapi:
            self.set_api_url()
            self.load_datasets()
        elif clicked == open_docs:
            try:
                # Try to open local docs if present
                docs_path = Path(__file__).resolve().parents[1] / 'docs' / 'RUNNING.md'
                if docs_path.exists():
                    try:
                        os.startfile(str(docs_path))
                    except Exception:
                        import webbrowser

                        webbrowser.open('file://' + str(docs_path))
                else:
                    # Fallback: open README
                    readme = Path(__file__).resolve().parents[1] / 'README.md'
                    if readme.exists():
                        try:
                            os.startfile(str(readme))
                        except Exception:
                            import webbrowser

                            webbrowser.open('file://' + str(readme))
            except Exception as e:
                print('open docs failed:', e)
        else:
            QtWidgets.QApplication.quit()


def headless_upload(csv_path, token, api_base=API_BASE):
    """Upload CSV in a headless mode for CI. Returns 0 on success, non-zero otherwise."""
    try:
        with open(csv_path, 'rb') as fh:
            files = {'file': (os.path.basename(csv_path), fh, 'text/csv')}
            headers = {}
            if token:
                headers['Authorization'] = f'Token {token}'
            res = requests.post(f'{api_base}/upload/', files=files, headers=headers, timeout=60)
            print('Status:', res.status_code)
            try:
                print('Response JSON:', res.json())
            except Exception:
                print('Response text:', res.text)
            if res.status_code == 200 and res.json().get('created', 0) > 0:
                print('Headless upload: success')
                return 0
            else:
                print('Headless upload: failed or no rows created')
                return 2
    except Exception as e:
        print('Headless upload error:', e)
        return 3


if __name__ == '__main__':
    # Headless upload mode for CI and automation
    if '--upload-ci' in sys.argv:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--upload-ci', action='store_true', help='internal CI flag')
        parser.add_argument('--csv', required=True)
        parser.add_argument('--token', required=True)
        parser.add_argument('--api', default=API_BASE)
        args = parser.parse_args(sys.argv[1:])
        rc = headless_upload(args.csv, args.token, args.api)
        sys.exit(rc)

    # Allow a headless smoke test for CI and packaging validation
    if '--smoke' in sys.argv:
        print('smoke-check: imports OK')
        sys.exit(0)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(THEME_CSS)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())