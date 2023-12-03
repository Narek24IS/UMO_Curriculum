import os
import sys

from PyQt6.QtWidgets import QApplication

from database import PlanDatabase
from interface.MainWindow import MainWindow
from plan_parse import Plan


def load_files_to_database(path: str, db: PlanDatabase) -> None:
    """
    Функция для перебора каталога, нахождения всего файлов с планом в нём и их парсинг
    Не используется по причине отсутствия единой структуры во всех файлах
    path - путь к папке с файлами учебного плана
    db - объект интерфейса базы данных
    """
    directory = path
    # Обходит все объекты в директории
    for root, dirs, files in os.walk(directory):
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
                    db.insert_plan(plan)
                    print(f'План специальности "{plan.name}" добавлен в базу данных')
                except:
                    print(f'Файл "{file}" не удалось обработать. Неправильный шаблон файла!')
                    continue


if __name__=='__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


