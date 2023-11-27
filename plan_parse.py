import openpyxl
from openpyxl.cell.cell import Cell
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from classes import ControlForm, TotalHours, Required, Semester, Discipline


class Plan:
    def __init__(self, file_path: str):
        self.worksheet = self.open_worksheet_in_file(file_path)
        self.disciplines: list[Discipline] = self.get_disciplines()

    def open_worksheet_in_file(self, file_path: str) -> Worksheet:
        # Загрузка файла Excel
        self.workbook: Workbook = openpyxl.load_workbook(file_path)
        # Получение листа по имени
        return self.workbook['План']

    @staticmethod
    def is_bold(cell: Cell) -> bool:
        return cell.font.bold

    @staticmethod
    def check_value_and_split(value: str | None) -> list[int] | None:
        if value:
            return [int(x) for x in value]
        else:
            return None

    @staticmethod
    def check_int(value: str | None) -> int | None:
        if value:
            return int(value)
        else:
            return None

    def get_semesters_from_row(self, row: list[str]) -> list[Semester]:
        semesters: list[Semester] = []
        row = row[17:]

        for i in range(0, len(row), 9):
            if row[i]:
                num = i // 9 + 1
                total = self.check_int(row[i])
                lek = self.check_int(row[i + 1])
                lab = self.check_int(row[i + 2])
                pr = self.check_int(row[i + 3])
                krp = self.check_int(row[i + 4])
                ip = self.check_int(row[i + 5])
                sr = self.check_int(row[i + 6])
                cons = self.check_int(row[i + 7])
                patt = self.check_int(row[i + 8])
                semesters.append(Semester(num, total, lek, lab, pr, krp, ip, sr, cons, patt))

        return semesters

    def get_control_form(self, row: list[str]) -> ControlForm:
        ekz_sem = self.check_value_and_split(row[3])
        zach_sem = self.check_value_and_split(row[4])
        zach0_sem = self.check_value_and_split(row[5])
        kp_sem = self.check_value_and_split(row[6])
        kr_sem = self.check_value_and_split(row[7])
        dr_sem = self.check_value_and_split(row[8])

        return ControlForm(ekz_sem, zach_sem, zach0_sem, kp_sem, kr_sem, dr_sem)

    def get_total_hours(self, row: list[str]) -> TotalHours:
        expert = self.check_int(row[9])
        plan = self.check_int(row[10])
        with_teacher = self.check_int(row[11])
        ip = self.check_int(row[12])
        sr = self.check_int(row[13])
        patt = self.check_int(row[14])

        return TotalHours(expert, plan, with_teacher, ip, sr, patt)

    def get_required(self, row: list[str]) -> Required:
        important = self.check_int(row[15])
        not_important = self.check_int(row[16])

        return Required(important, not_important)

    def get_disciplines(self) -> list[Discipline]:
        row: tuple[Cell]
        disciplines: list[Discipline] = []
        for row in self.worksheet.iter_rows(min_row=6, max_row=self.worksheet.max_row):
            if self.is_bold(row[2]) or row[2].value is None:
                continue
            row: list[str] = [cell.value for cell in row]

            # Получение форм контроля
            control_form = self.get_control_form(row)
            # Получение общего кол-ва часов
            total_hours = self.get_total_hours(row)
            # Получение обязательной программы
            required = self.get_required(row)
            # Получение семестров, в которых будут формы контроля
            semesters = self.get_semesters_from_row(row)

            # Получение индекса, названия и статуса дисциплины
            in_plan = True if row[0] == '+' else False
            ind = row[1]
            name = row[2]
            disciplines.append(Discipline(in_plan, ind, name, control_form, total_hours, required, semesters))

        return disciplines


plan = Plan('Plan.xlsx')
