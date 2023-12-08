import os
import sys

from PyQt6.QtWidgets import QApplication

from database import PlanDatabase
from interface.MainWindow import MainWindow
from plan_parse import Plan

if __name__=='__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


