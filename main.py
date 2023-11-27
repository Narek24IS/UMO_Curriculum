from plan_parse import Plan
from database import PlanDatabase

if __name__=='__main__':
    # Парсим файл с планом
    plan = Plan('Plan.xlsx')
    # Создаём БД, в который будем загружать данные
    db = PlanDatabase('planDB.sqlite')
    # Перебор всех дисциплин в плане и добавление их в базу данных
    for discipline in plan.disciplines:
        db.insert_discipline(discipline)