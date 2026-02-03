import os
import sys

# Runtime hook to set QT_PLUGIN_PATH when running from a PyInstaller onefile bundle.
# PyInstaller extracts bundled files to sys._MEIPASS; plugins are placed under
# a PyQt5/Qt/plugins directory when collected via collect_qt_plugins.
if getattr(sys, '_MEIPASS', None):
    meipass = sys._MEIPASS
    plugin_path = os.path.join(meipass, 'PyQt5', 'Qt', 'plugins')
    if os.path.isdir(plugin_path):
        os.environ['QT_PLUGIN_PATH'] = plugin_path
