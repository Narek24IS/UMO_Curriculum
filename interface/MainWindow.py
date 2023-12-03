import os
import sys

import openpyxl
from PyQt6.QtSql import QSqlQuery, QSqlDatabase
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QApplication, QCheckBox, QTableWidgetItem, QMessageBox

from database import PlanDatabase
from interface.UI_MainWindow import Ui_MainWindow
from plan_parse import Plan


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.result: list[list] = [[0]]

        self.db_connect('planDB.sqlite')
        # Получение результата запроса
        self.query.exec(f'SELECT * FROM All_data;')

        self.ui.tabWidget.setCurrentIndex(0)

        self.ui.infoLabel.setText("Если вы впервые открыли программу, то следуйте инструкции ниже:\n"
                             "1. Нажмите на кнопку 'Выбрать папку'\n"
                             "2. Выберите папку с файлами с учебным планом и нажмите 'Открыть'\n"
                             "3. Нажмите на кнопку 'Обработать файлы'\n"
                             "3. Нажмите 'OK' и ждите, ничего не нажимая, даже если вылезет ошибка\n"
                             "4. Всё готово!\n\n"
                             "Вы можете выбрать какая вам нужна информация во второй\n"
                             "вкладке и посмотреть результаты в третьей вкладке.\n"
                             "Вы также можете экспортировать текущую таблицу в Excel\n"
                             "нажав на кнопку 'Экспортировать в Excel' на третьей вкладке и введите имя файла.")

        self.ui.select_btn.clicked.connect(self.open_select_dialog)
        self.ui.proc_btn.clicked.connect(self.load_files_to_database)
        self.ui.tabWidget.tabBarClicked.connect(self.refresh_table)
        self.ui.export_btn.clicked.connect(self.export_table_to_xlsx)

    def db_connect(self, db_name: str = 'MyDatabase'):
        self.db_con = QSqlDatabase.addDatabase('QSQLITE')
        self.db_con.setDatabaseName(db_name)
        self.query = QSqlQuery(self.db_con)

        if not self.db_con.open():
            print(f"Database Error: {self.db_con.lastError().databaseText()}")
            sys.exit(1)

    def open_select_dialog(self):
        file_dialog = QFileDialog()
        self.path = file_dialog.getExistingDirectory(self, "Выбрать", "")
        self.db = PlanDatabase('planDB.sqlite', new_db=True)

    def create_view(self):
        self.db.create_view()
        self.query.exec(f'SELECT * FROM All_data;')
        self.ui.proc_btn.setText('Обработать файлы')

        self.show_message('Обработка файлов окончена', self.report)

    def load_files_to_database(self):
        try:
            success_files = []
            error_files = []
            if self.path:
                self.ui.proc_btn.setText('Обработка...')
                self.show_message('Идёт обработка', "Не закрывайте приложение, идёт обработка файлов!\n"
                                                    "Для продолжения работы нажмите 'OK'")

            for root, dirs, files in os.walk(self.path):
                for file in files:
                    # Если формат файла - xlsx
                    if file.endswith('.xlsx'):
                        # Получение полного пути к файлу
                        file_path = os.path.join(root, file)
                        # Пробуем через try except, на случай ошибки, распарсить файл
                        try:
                            # Парсим файл с планом
                            plan = Plan(file_path)
                            # Вставляем данные из файла в БД
                            self.db.insert_plan(plan)
                            success_files.append(f"{plan.name} {str(plan.start_year)}")
                            print(plan.name)
                        except Exception as error:
                            print(f"{type(error).__name__}: {error}")
                            error_files.append(file)

            self.report = (f"В базу данных добавлены планы:\n"
                           + '\n'.join(success_files)
                           + "\n\nЭти файлы не удалось обработать из-за неправильной структуры файла:\n"
                           + '\n'.join(error_files))

            self.create_view()

        except AttributeError as error:
            print(f"{type(error).__name__}: {error}")
            self.show_message("Выберите папку", "Сначала выберите папку с файлами!")

    def show_message(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    def get_need_attrs(self):
        # Получаем индексы и названия нужных атрибутов
        # Добавляем в список result записи
        self.need_atr: {int: str} = {}

        # Очищаем список от прошлого результата
        if self.result:
            self.result.clear()

        # Проверяем чекбоксы в первом столбце
        for ind, child_widget in enumerate(self.ui.planAttrsGB.children()):
            if isinstance(child_widget, QCheckBox) and child_widget.isChecked():
                self.need_atr[ind - 1] = child_widget.text()

        # Проверяем чекбоксы во втором столбце
        for ind, child_widget in enumerate(self.ui.disciplineAttrsGB.children()):
            if isinstance(child_widget, QCheckBox) and child_widget.isChecked():
                ind = ind + len(self.ui.planAttrsGB.children()) - 1
                self.need_atr[ind - 1] = child_widget.text()

        # Проверяем чекбоксы в третьем столбце
        for ind, child_widget in enumerate(self.ui.semesterAttrsGB.children()):
            if isinstance(child_widget, QCheckBox) and child_widget.isChecked():
                ind = ind + len(self.ui.planAttrsGB.children()) + len(self.ui.disciplineAttrsGB.children()) - 2
                self.need_atr[ind - 1] = child_widget.text()

        # Проходимся по всем записям и вытаскиваем нужные данные
        if self.query.first():
            self.result.append([self.query.value(i) for i in self.need_atr.keys()])

        while self.query.next():
            self.result.append([self.query.value(i) for i in self.need_atr.keys()])

        # print(len(self.result[0]), len(self.result))

    def set_table_prop(self):
        # Количество строк и столбцов
        row = len(self.result)
        # print(self.result)
        try:
            col = len(self.result[0])
        except IndexError:
            col = 0
        if not col:
            row = 0
        self.ui.tableWidget.setRowCount(row)
        self.ui.tableWidget.setColumnCount(col)

        # Заголовок
        self.column_headers = self.need_atr.values()
        self.ui.tableWidget.setHorizontalHeaderLabels(self.column_headers)
        self.ui.tableWidget.horizontalHeader().setStretchLastSection(True)

    def insert_values_to_table(self):
        # Заполнение таблицы
        for row, result in enumerate(self.result):
            for column, value in enumerate(result):
                item = QTableWidgetItem(str(value))
                self.ui.tableWidget.setItem(row, column, item)

        # Изменение размеров строк и столбцов
        # self.ui.tableWidget.resizeColumnsToContents()
        self.ui.tableWidget.resizeRowsToContents()

    def refresh_table(self):
        self.get_need_attrs()
        self.set_table_prop()
        self.insert_values_to_table()

    def get_new_file_name(self) -> str:
        file_dialog = QFileDialog(self)
        # options = QFileDialog.options(QFileDialog())
        # options |= options.DontUseNativeDialog  # Используем диалог Qt, а не системный

        # Получаем путь к директории проекта
        executable_path = sys.argv[0]
        project_directory = os.path.dirname(os.path.abspath(executable_path))

        file_name: str
        file_name, _ = file_dialog.getSaveFileName(
            self,
            "Сохранить файл",
            project_directory,
            "Файлы Excel (*.xlsx)",
            # options=options
        )

        if file_name:
            if file_name.endswith('.xlsx'):
                return file_name
            else:
                return file_name + '.xlsx'
        else:
            return 'Output.xlsx'

    def export_table_to_xlsx(self):
        wb = openpyxl.Workbook()

        sheet = wb.active

        sheet.append(list(self.column_headers))

        # Заполнение таблицы
        for row in self.result:
            sheet.append(row)

        file_path = self.get_new_file_name()
        wb.save(file_path)
        wb.close()
        file_name = file_path.split('/')[-1]
        self.show_message("Файл сохранён", f"Файл {file_name} успешно сохранён"
                                           f" по пути {file_path}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
