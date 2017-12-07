import sys

from PyQt5.Qt import QApplication

from controllers.app import AppWidget

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app_widget = AppWidget()
    sys.exit(app.exec_())
