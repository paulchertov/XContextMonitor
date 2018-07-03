import sys
import os

from PyQt5.Qt import QApplication

from controllers.app import AppWidget

if __name__ == '__main__':
    # remove old database if exists
    db_path = os.path.join(os.path.curdir, "db.db")
    if os.path.isfile(db_path):
        os.remove(db_path)

    app = QApplication(sys.argv)
    app_widget = AppWidget()
    sys.exit(app.exec_())
