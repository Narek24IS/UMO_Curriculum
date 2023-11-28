import openpyxl
from openpyxl.cell.cell import Cell
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from classes import ControlForm, TotalHours, RequiredHours, Semester, Discipline


class Plan:
    def __init__(self, file_path: str):
        self.worksheet = self.open_worksheet_in_file(file_path)
        self.get_title_info()
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

    def get_control_form(self, row: list[str], sem_num:int) -> ControlForm:
        sem = None
        col = 3
        while sem is None and col < 9:
            sem = self.check_value_and_split(row[col])
            col += 1

        if sem is not None and sem_num in sem:
            match col:
                case 3:
                    return ControlForm.EKZ
                case 4:
                    return ControlForm.ZACH
                case 5:
                    return ControlForm.ZACH0
                case 6:
                    return ControlForm.KP
                case 7:
                    return ControlForm.KR
                case 8:
                    return ControlForm.DR
                case _:
                    return ControlForm.NO
        else:
            return ControlForm.NO

    def get_semesters_from_row(self, row: list[str]) -> list[Semester]:
        semesters: list[Semester] = []
        sem_row = row[17:]

        for i in range(0, len(sem_row)-2, 9):
            if sem_row[i]:
                num = i // 9 + 1
                total = self.check_int(sem_row[i])
                lek = self.check_int(sem_row[i + 1])
                lab = self.check_int(sem_row[i + 2])
                pr = self.check_int(sem_row[i + 3])
                krp = self.check_int(sem_row[i + 4])
                ip = self.check_int(sem_row[i + 5])
                sr = self.check_int(sem_row[i + 6])
                cons = self.check_int(sem_row[i + 7])
                patt = self.check_int(sem_row[i + 8])
                control = self.get_control_form(row, num)
                semesters.append(Semester(num, total, lek, lab, pr, krp, ip, sr, cons, patt, control))

        return semesters

    def get_total_hours(self, row: list[str]) -> TotalHours:
        expert = self.check_int(row[9])
        plan = self.check_int(row[10])
        with_teacher = self.check_int(row[11])
        ip = self.check_int(row[12])
        sr = self.check_int(row[13])
        patt = self.check_int(row[14])

        return TotalHours(expert, plan, with_teacher, ip, sr, patt)

    def get_required(self, row: list[str]) -> RequiredHours:
        important = self.check_int(row[15])
        not_important = self.check_int(row[16])

        return RequiredHours(important, not_important)

    def get_disciplines(self) -> list[Discipline]:
        row: tuple[Cell]
        disciplines: list[Discipline] = []
        for row in self.worksheet.iter_rows(min_row=6, max_row=self.worksheet.max_row):
            if self.is_bold(row[2]) or row[2].value is None:
                continue
            row: list[str] = [cell.value for cell in row]

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
            disciplines.append(Discipline(in_plan, ind, name, total_hours, required, semesters))

        return disciplines


    def get_title_info(self):
        title_worksheet = self.workbook['Титул']
        cell_value_list = title_worksheet['D29'].value.split()
        if '_x000d_' in cell_value_list:
            cell_value_list.remove('_x000d_')
        ind = cell_value_list.index('Профиль')
        self.name = ' '.join(cell_value_list[:ind])
        self.cafedra = title_worksheet['D37'].value
        self.facultet = title_worksheet['D38'].value
        self.profile = ' '.join(cell_value_list[ind+10:])
        self.cod = title_worksheet['D27'].value
        self.kvalik = title_worksheet['C40'].value.split(':')[1]
        self.edu_form = title_worksheet['C42'].value.split(':')[1]
        self.start_year = int(title_worksheet['W40'].value)
        self.standart = title_worksheet['W42'].value
        self.baza = title_worksheet['C44'].value.split(':')[1]

pl = Plan('Plans/Plan.xlsx')
