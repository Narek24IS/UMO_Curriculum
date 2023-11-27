import sqlite3

class PlanDatabase:
    def __init__(self, db_path='plan_database.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Discipline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                required_not_important_hours INTEGER
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Semester (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discipline_id INTEGER,
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
                is_ekz BOOL,
                is_zach BOOL,
                is_zach0 BOOL,
                is_kp BOOL,
                is_kr BOOL,
                is_dr BOOL,
                FOREIGN KEY (discipline_id) REFERENCES Discipline (id)
            )
        ''')
        self.conn.commit()

    def insert_discipline(self, discipline):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO Discipline (
                in_plan, ind, name,
                control_form_ekz_sem, control_form_zach_sem, control_form_zach0_sem,
                control_form_kp_sem, control_form_kr_sem, control_form_dr_sem,
                total_hours_expert, total_hours_plan, total_hours_with_teacher,
                total_hours_ip, total_hours_sr, total_hours_patt,
                required_important, required_not_important
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            discipline.in_plan, discipline.ind, discipline.name,
            discipline.control_form.ekz_sem, discipline.control_form.zach_sem, discipline.control_form.zach0_sem,
            discipline.control_form.kp_sem, discipline.control_form.kr_sem, discipline.control_form.dr_sem,
            discipline.total_hours.expert, discipline.total_hours.plan, discipline.total_hours.with_teacher,
            discipline.total_hours.ip, discipline.total_hours.sr, discipline.total_hours.patt,
            discipline.required.important, discipline.required.not_important
        ))
        discipline_id = cursor.lastrowid
        for semester in discipline.semesters:
            self.insert_semester(discipline_id, semester)
        self.conn.commit()

    def insert_semester(self, discipline_id, semester):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO Semester (
                discipline_id, num, total, lek, lab, pr, krp, ip, sr, cons, patt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            discipline_id, semester.num, semester.total,
            semester.lek, semester.lab, semester.pr,
            semester.krp, semester.ip, semester.sr,
            semester.cons, semester.patt
        ))

db = PlanDatabase('planDB.sqlite')