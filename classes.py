import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from xml.dom.minidom import Element

@dataclass
class ControlForm:
    # разделить по цифрам!!!!!
    # В каких семестрах будут экзамены
    ekz_sem: list[int] | None = None
    # В каких семестрах будут зачёты
    zach_sem: list[int] | None = None
    # В каких семестрах будут зачёты
    zach_sem0: list[int] | None = None
    # В каких семестрах будут курсовые практики
    kp_sem: list[int] | None = None
    # В каких семестрах будут контрольные работы
    kr_sem: list[int] | None = None
    # В каких семестрах будут другие формы контроля
    dr_sem: list[int] | None = None

@dataclass
class TotalHours:
    # Кол-во необходимых часов по экспертному мнению
    expert: int
    # Всего часов по плану
    plan: int
    # Количество часов проводимых с преподавателем
    with_teacher: int
    # Количество часов выделенных на индивидуальные проект
    ip: int
    # Количество часов выделенных на самостоятельную работу
    sr: int
    # Количество часов выделенных на предпрофессиональную аттестацию
    patt: int

@dataclass
class Required:
    important: int
    not_important: int

@dataclass
class Semester:
    # Номер семестра
    num: int
    # Всего часов в семестре
    total: int
    # Количество часов выделенных на лекции
    lek: int
    # Количество часов выделенных на лабораторные работы
    lab: int
    # Количество часов выделенных на практические работы
    pr: int
    # Количество часов выделенных на контрольные работы по практике
    krp: int
    # Количество часов выделенных на индивидуальные проект
    ip: int
    # Количество часов выделенных на самостоятельную работу
    sr: int
    # Количество часов выделенных на консультацию с преподавателем
    cons: int
    # Количество часов выделенных на предпрофессиональную аттестацию
    patt: int

class Discipline:
    def __init__(self, in_plan: bool, ind: str, name: str, control_form: ControlForm,
                 total_hours: TotalHours, required: Required, semesters: list[Semester]):
        # Считать ли в плане
        self.in_plan = in_plan
        # Индекс дисциплины
        self.ind = ind
        # Название дисциплины
        self.name = name
        # Формы контроля и в каком семестре
        self.control_form = control_form
        # Количество часов за всё время обучения
        self.total_hours = total_hours
        # Объём обязательной программы
        self.required = required
        # В каких семестрах будет вестись данная дисциплина и по сколько часов
        self.semesters = semesters

    def __str__(self):
        return (f'{self.in_plan} {self.ind} {self.name} {self.control_form} {self.total_hours}'
                f'{self.required} {self.semesters}')
