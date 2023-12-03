import sqlite3

from classes import Discipline, Semester
from plan_parse import Plan


class PlanDatabase:
    """Класс, который создаёт БД и имеет методы, которые являются интерфейсами этой БД"""

    def __init__(self, db_path='plan_database.db', new_db: bool = False):
        self.conn = sqlite3.connect(db_path)
        # Если флаг имеет значение True удаляются все таблица, создаются по новой и заполняются нужными данными
        if new_db:
            self.drop_tables()
            self.create_tables()
            self.insert_control_form()
        # Проверят созданы ли все таблицы и создаёт их в противном случае
        self.create_tables()

    def create_tables(self):
        """Создание всех таблиц в БД, если их нет"""
        cursor = self.conn.cursor()
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Plan(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        cafedra TEXT,
                        facultet TEXT,
                        profile TEXT,
                        cod TEXT,
                        kvalik TEXT,
                        edu_form TEXT,
                        start_year INT,
                        standart TEXT,
                        baza TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Discipline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INT,
                in_plan BOOL,
                ind TEXT,
                name TEXT,
                total_hours_expert INTEGER,
                total_hours_plan INTEGER,
                total_hours_with_teacher INTEGER,
                total_hours_ip INTEGER,
                total_hours_sr INTEGER,
                total_hours_patt INTEGER,
                required_important_hours INTEGER,
                required_not_important_hours INTEGER,
                FOREIGN KEY (plan_id) REFERENCES Plan (id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ControlForm (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Semester (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discipline_id INTEGER,
                control_form_id INTEGER,
                num INTEGER,
                total INTEGER,
                lek INTEGER,
                lab INTEGER,
                pr INTEGER,
                krp INTEGER,
                ip INTEGER,
                sr INTEGER,
                cons INTEGER,
                patt INTEGER,
                FOREIGN KEY (discipline_id) REFERENCES Discipline (id),
                FOREIGN KEY (control_form_id) REFERENCES ControlForm (id)
            )
        ''')
        self.conn.commit()

    def insert_control_form(self):
        """Вставляет в таблицу ControlForm все существующие формы контроля"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO ControlForm (name)
            VALUES("Экзамен"), ("Зачёт"), ("Зачёт с оценкой"), 
            ("Курсовая практика"), ("Контрольная работа"), ("Другое")
            ''')
        self.conn.commit()

    def insert_plan(self, plan: Plan):
        """Вставляет все данные из объекта класса Plan в БД"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO Plan(
                 name, facultet, cafedra, profile, cod, kvalik,
                 edu_form, start_year, standart, baza
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            plan.name, plan.facultet, plan.cafedra, plan.profile, plan.cod,
            plan.kvalik, plan.edu_form, plan.start_year,
            plan.standart, plan.baza
        ))
        plan_id = cursor.lastrowid
        # Перебирает все дисциплины в плане и вставляет их в БД
        for discipline in plan.disciplines:
            self.insert_discipline(int(plan_id), discipline)
        self.conn.commit()

    def insert_discipline(self, plan_id: int, discipline: Discipline):
        """Вставляет все данные из объекта класса Discipline в БД"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO Discipline (
                in_plan, ind, name, plan_id,
                total_hours_expert, total_hours_plan, total_hours_with_teacher,
                total_hours_ip, total_hours_sr, total_hours_patt,
                required_important_hours, required_not_important_hours
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            discipline.in_plan, discipline.ind, discipline.name, plan_id,
            discipline.total_hours.expert, discipline.total_hours.plan, discipline.total_hours.with_teacher,
            discipline.total_hours.ip, discipline.total_hours.sr, discipline.total_hours.patt,
            discipline.required.important, discipline.required.not_important
        ))
        discipline_id = cursor.lastrowid
        # Перебирает все семестры в дисциплине и вставляет их в БД
        for semester in discipline.semesters:
            self.insert_semester(discipline_id, semester)
        self.conn.commit()

    def insert_semester(self, discipline_id: int, semester: Semester):
        """Вставляет все данные из объекта класса Semester в БД"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO Semester (
                discipline_id, control_form_id, num, total, lek, lab, pr, krp, ip, sr, cons, patt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            discipline_id, semester.control_form.value, semester.num, semester.total,
            semester.lek, semester.lab, semester.pr,
            semester.krp, semester.ip, semester.sr,
            semester.cons, semester.patt
        ))
        self.conn.commit()

    def create_view(self):
        cursor = self.conn.cursor()
        cursor.execute('''drop view if exists All_data;''')
        cursor.execute('''
        create view All_data as
        select P.name Направление, P.cafedra Кафедра, P.facultet Факультет, P.profile Профиль,
           P.cod Код_специальности, P.kvalik Квалификация, P.edu_form Форма_обучения,
           P.start_year Год_начала, P.standart Стандарт_ФГОС, P.baza База,
           D.in_plan В_плане, D.ind Индекс_дисциплины, D.name Дисциплина,
           D.total_hours_expert Экспертное, D.total_hours_plan По_плану, D.total_hours_with_teacher С_препод,
           D.total_hours_ip ИП, D.total_hours_sr СР, D.total_hours_patt ПАтт,
           D.required_important_hours `Обяз. часть`, D.required_not_important_hours `Вар. часть`,
           S.num Семестр, S.total Всего, S.lek Лек, S.lab Лаб, S.pr Пр, S.krp Крп, S.ip ИП,
           S.sr СР, S.cons Конс, S.patt ПАтт, CF.name Форма_контроля
        from Plan P
             join main.Discipline D on P.id = D.plan_id
             join main.Semester S on D.id = S.discipline_id
             join main.ControlForm CF on S.control_form_id = CF.id;''')

    def drop_tables(self):
        """Удаляет все имеющиеся в БД таблицы"""
        cursor = self.conn.cursor()
        cursor.execute('''
            drop table if exists ControlForm;
            ''')
        cursor.execute('''
            drop table if exists Plan;
            ''')
        cursor.execute('''
            drop table if exists Discipline;
            ''')
        cursor.execute('''
            drop table if exists Semester;
            ''')

        self.conn.commit()
