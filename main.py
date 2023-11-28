from plan_parse import Plan
from database import PlanDatabase
import os

def load_files_to_database(path:str, db: PlanDatabase):
    # Функция для перебора каталога, нахождения всег файлов с планом в нём и их парсинг
    # Не используется по причине отсутствия единой структуры во всех файлах
    directory = path
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.xlsx'):
                file_path = os.path.join(root, file)
                try:
                    # Парсим файл с планом
                    plan = Plan(file_path)
                    # Вставляем данные из файла в БД
                    db.insert_plan(plan)
                    print(f'План специальности "{plan.name}" добавлен в базу данных')
                except:
                    print(f'Файл "{file}" не удалось обработать')
                    continue



if __name__=='__main__':
    # # Парсим файл с планом
    # plan = Plan('Plan.xlsx')
    # # Создаём БД, в который будем загружать данные
    # db = PlanDatabase('planDB.sqlite')
    # # Вставляем данные из файла в БД
    # db.insert_plan(plan)
    # Создаём БД, в который будем загружать данные
    db = PlanDatabase('planDB.sqlite', new_db = True)
    load_files_to_database('Plans', db)

