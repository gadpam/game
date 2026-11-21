# -*- coding: utf-8 -*-
"""
Фактура по группе П32.

Источники:
  1) «Сводная ведомость успеваемости за сентябрь–октябрь 2026–2027 уч. год»
     Полоцкий государственный экономический колледж, группа П32
     (дневная форма, специальность «Разработка и сопровождение
     программного обеспечения информационных систем»).
     Из ведомости взяты отметки каждого ученика по восьми предметам.
  2) Журнал КПиЯП, V семестр — отметки «зач» по лабораторным работам.
     Снято из файла журнала (КПиЯП, 15 лабораторных, 13 лекций).

Всё, что можно посчитать, считается здесь — из отметок. Значения из
ведомости сохранены как эталон и сверяются функцией check_sources():
средний балл, признаки успеваемости, уровень и сводка по предметам.
"""
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, List, NamedTuple, Tuple

COLLEGE = "Полоцкий государственный экономический колледж"
GROUP = "П32"
SPECIALTY = "Разработка и сопровождение программного обеспечения информационных систем"
TEACHER = "Барило С. С."
PERIOD = "сентябрь–октябрь 2026/2027"
SUBJECT = "КПиЯП"

STUDENTS_TOTAL = 23

NA = "н/а"
ZACH = "зач"

# ── предметы в порядке колонок ведомости
#    (название, абсолютная успеваемость %, средний балл, качественная %)
SUBJECTS: List[Tuple[str, int, float, int]] = [
    ("Физ-ра и здоровье", 100, 8.81, 100),
    ("ТПО", 91, 5.95, 52),
    ("ТРПО", 78, 4.41, 17),
    ("КПиЯП", 52, 4.00, 39),
    ("Ин. яз (проф. лексик)", 100, 7.87, 78),
    ("ТКиОК", 100, 8.48, 100),
    ("ПССиП", 65, 5.00, 57),
    ("СУБД", 96, 6.95, 74),
]
SUBJECT_SHORT = ["Физ-ра", "ТПО", "ТРПО", "КПиЯП", "Ин. яз", "ТКиОК", "ПССиП", "СУБД"]

# ── эталон из ведомости: фамилия → (средний балл, абс. успеваемость +,
#    качественная успеваемость +, соответствие уровню)
VEDOMOST: Dict[str, Tuple[float, bool, bool, int]] = {
    "Александрович": (4.57, False, False, 2),
    "Богородь": (3.43, False, False, 2),
    "Буткевич А. В.": (7.50, True, False, 3),
    "Буткевич Д. Н.": (4.14, False, False, 3),
    "Горбатенко": (3.75, False, False, 3),
    "Гражевская": (6.75, False, False, 3),
    "Дайлидович": (5.43, False, False, 3),
    "Карсацкая": (6.88, False, False, 3),
    "Ловейкина": (8.50, True, True, 4),
    "Максимович": (6.63, True, False, 3),
    "Маланочкин": (7.88, True, False, 3),
    "Миньков": (4.75, False, False, 3),
    "Папко": (8.25, True, True, 4),
    "Садоха": (7.00, True, False, 3),
    "Свистун": (6.75, False, False, 3),
    "Семенцов": (7.88, True, False, 3),
    "Слыщенко": (4.63, False, False, 3),
    "Тарасенко": (6.75, False, False, 3),
    "Федуро": (6.88, True, False, 2),
    "Хандусь": (4.50, False, False, 3),
    "Ходарович": (8.38, True, True, 4),
    "Хоменок": (9.00, True, True, 4),
    "Шантирова": (7.25, True, False, 3),
}

# ── отметки из ведомости: 8 предметов + число сданных лабораторных (журнал)
RAW: List[Tuple[str, str, Tuple[str, ...], int]] = [
    ("Александрович", "К. С.", ("8", "5", "4", NA, "6", "9", NA, ZACH), 3),
    ("Богородь", "А. М.", (ZACH, NA, NA, NA, "6", "9", "6", "3"), 4),
    ("Буткевич", "А. В.", ("10", "5", "6", "9", "7", "9", "7", "7"), 15),
    ("Буткевич", "Д. Н.", ("9", ZACH, "5", NA, "6", "9", NA, NA), 0),
    ("Горбатенко", "В. К.", ("9", NA, NA, NA, "6", "8", NA, "7"), 0),
    ("Гражевская", "Н. А.", ("9", "9", "5", NA, "10", "8", "7", "6"), 0),
    ("Дайлидович", "И. Е.", (ZACH, "7", "5", NA, "9", "9", NA, "8"), 1),
    ("Карсацкая", "В. Я.", ("8", "7", "6", NA, "8", "9", "9", "8"), 1),
    ("Ловейкина", "В. М.", ("8", "7", "7", "9", "9", "9", "10", "9"), 10),
    ("Максимович", "А. А.", ("7", "5", "6", "7", "6", "8", "7", "7"), 10),
    ("Маланочкин", "М. С.", ("9", "6", "6", "9", "9", "8", "8", "8"), 15),
    ("Миньков", "Н. М.", ("10", "5", NA, NA, "8", "9", NA, "6"), 1),
    ("Папко", "Д. Е.", ("10", "8", "7", "9", "8", "8", "7", "9"), 15),
    ("Садоха", "Д. А.", ("8", "7", "5", "5", "8", "8", "8", "7"), 6),
    ("Свистун", "Е. Е.", ("8", "7", "6", NA, "9", "8", "9", "7"), 0),
    ("Семенцов", "А. В.", ("9", "8", "6", "8", "9", "8", "6", "9"), 6),
    ("Слыщенко", "Е. Д.", ("8", "6", NA, NA, "8", "8", NA, "7"), 2),
    ("Тарасенко", "Н. М.", ("8", "7", "6", "9", "8", "9", NA, "7"), 5),
    ("Федуро", "Д. Д.", ("9", "6", "4", "5", "8", "8", "9", "6"), 3),
    ("Хандусь", "Г. Г.", ("9", "5", NA, NA, "7", "9", NA, "6"), 1),
    ("Ходарович", "Н. А.", ("10", "7", "7", "8", "9", "9", "9", "8"), 8),
    ("Хоменок", "Д. Ф.", ("10", "8", ZACH, "9", "9", "8", ZACH, "10"), 11),
    ("Шантирова", "Д. Д.", ("9", "6", "6", "5", "8", "8", "8", "8"), 5),
]


# ─────────────────────────────────────────────────── правила ведомости
#  * «н/а» — отметки нет: в сумму идёт ноль, в знаменатель — тоже;
#  * «зач» — отметки нет, но работа зачтена: из знаменателя выпадает;
#  * средний балл = сумма отметок ÷ (число предметов − число «зач»);
#  * качественная успеваемость (предмет) = отметки 7–10 и «зач»;
#  * признак «+» абсолютной успеваемости — нет ни одного «н/а»;
#  * признак «+» качественной успеваемости — все отметки 7–10 и «зач»;
#  * соответствие уровню: 4 — все отметки 7–10, 2 — есть 4 или ниже, иначе 3.

def _round2(value: float) -> float:
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _is_num(mark: str) -> bool:
    return mark.isdigit()


def _grade(mark: str) -> int:
    return int(mark) if mark.isdigit() else 0


def student_avg(marks: Tuple[str, ...]) -> float:
    total = sum(_grade(m) for m in marks)
    denom = len(marks) - sum(1 for m in marks if m == ZACH)
    return _round2(total / denom) if denom else 0.0


def mark_zone(mark: str) -> str:
    """Зона отметки: good — качественная (7–10, зач), mid — 4–6, low — 2–3, none — н/а."""
    if mark == NA:
        return "none"
    if mark == ZACH:
        return "good"
    g = _grade(mark)
    if g >= 7:
        return "good"
    if g >= 4:
        return "mid"
    return "low"


class Student(NamedTuple):
    """Одна строка ведомости + сдача лабораторных из журнала."""

    fam: str
    ini: str
    marks: Tuple[str, ...]   # 8 предметов: отметка, «зач» или «н/а»
    labs: int                # сдано лабораторных из 15
    avg: float               # средний балл по всем предметам
    abs_ok: bool             # признак абсолютной успеваемости («+»)
    qual_ok: bool            # признак качественной успеваемости («+»)
    level: int               # соответствие уровню (2 / 3 / 4)

    @property
    def full(self) -> str:
        return f"{self.fam} {self.ini}"

    @property
    def key(self) -> str:
        """Ключ эталона: фамилия, а при одинаковых фамилиях — фамилия с инициалами."""
        return f"{self.fam} {self.ini}" if self.fam in _DUP_SURNAMES else self.fam


_DUP_SURNAMES = {fam for fam in {r[0] for r in RAW}
                 if sum(1 for r in RAW if r[0] == fam) > 1}


def _build() -> List[Student]:
    out = []
    for fam, ini, marks, labs in RAW:
        numeric = [_grade(m) for m in marks]
        abs_ok = NA not in marks
        qual_ok = all(mark_zone(m) == "good" for m in marks)
        level = 2 if any(0 < g <= 4 for g in numeric) else (4 if qual_ok else 3)
        out.append(Student(fam, ini, marks, labs, student_avg(marks), abs_ok, qual_ok, level))
    return out


STUDENTS: List[Student] = _build()

LABS_TOTAL = 15          # лабораторных работ по КПиЯП
LECTURES_TOTAL = 13      # лекций по КПиЯП
LABS_PASSED = 122        # сдано лабораторных по группе
ATTESTED_KPIAP = 12      # имеют отметку по КПиЯП (сентябрь–октябрь)
AVG_KPIAP = 4.00         # средний балл группы по КПиЯП


# ─────────────────────────────────────────────────── сводные числа
def labs_done(n: int) -> str:
    """Статус по сдаче лабораторных: ok / near / mid / zero."""
    return "ok" if n == LABS_TOTAL else ("near" if n >= 10 else ("mid" if n >= 1 else "zero"))


def bucket(n: int) -> str:
    return labs_done(n)


def count_by_labs() -> Dict[str, int]:
    out = {"ok": 0, "near": 0, "mid": 0, "zero": 0}
    for s in STUDENTS:
        out[labs_done(s.labs)] += 1
    return out


def count_low_avg(limit: float = 5.0) -> int:
    return sum(1 for s in STUDENTS if s.avg < limit)


def count_abs_ok() -> int:
    """Студенты без «н/а» по всем предметам — признак «+» абсолютной успеваемости."""
    return sum(1 for s in STUDENTS if s.abs_ok)


def count_qual_ok() -> int:
    """Студенты, у которых все отметки 7–10 (признак «+» качественной успеваемости)."""
    return sum(1 for s in STUDENTS if s.qual_ok)


def count_level(level: int) -> int:
    return sum(1 for s in STUDENTS if s.level == level)


def count_with_na() -> int:
    """Студенты, у которых есть хотя бы один «н/а» (нет абсолютной успеваемости)."""
    return sum(1 for s in STUDENTS if not s.abs_ok)


def subject_stats(idx: int) -> Dict[str, float]:
    """Пересчёт сводки по одному предмету прямо из отметок."""
    marks = [s.marks[idx] for s in STUDENTS]
    total = sum(_grade(m) for m in marks)
    denom = len(marks) - sum(1 for m in marks if m == ZACH)
    return {
        "abs_pct": round(100.0 * sum(1 for m in marks if m != NA) / len(marks)),
        "avg": _round2(total / denom) if denom else 0.0,
        "qual_pct": round(100.0 * sum(1 for m in marks if mark_zone(m) == "good") / len(marks)),
    }


def check_sources() -> List[str]:
    """Сверка вычисленных чисел с эталоном из ведомости. Пустой список — всё сходится."""
    problems: List[str] = []
    for s in STUDENTS:
        ref = VEDOMOST.get(s.key)
        if ref is None:
            problems.append(f"{s.full}: нет эталона в ведомости")
            continue
        avg, abs_ok, qual_ok, level = ref
        if abs(avg - s.avg) > 0.005:
            problems.append(f"{s.full}: средний балл {s.avg} ≠ {avg} из ведомости")
        if abs_ok != s.abs_ok:
            problems.append(f"{s.full}: признак абсолютной успеваемости не совпал")
        if qual_ok != s.qual_ok:
            problems.append(f"{s.full}: признак качественной успеваемости не совпал")
        if level != s.level:
            problems.append(f"{s.full}: уровень {s.level} ≠ {level} из ведомости")
    for i, (name, abs_p, avg, qual) in enumerate(SUBJECTS):
        st = subject_stats(i)
        if st["abs_pct"] != abs_p:
            problems.append(f"{name}: успеваемость {st['abs_pct']}% ≠ {abs_p}%")
        if abs(st["avg"] - avg) > 0.005:
            problems.append(f"{name}: средний балл {st['avg']} ≠ {avg}")
        if st["qual_pct"] != qual:
            problems.append(f"{name}: качественная {st['qual_pct']}% ≠ {qual}%")
    if sum(s.labs for s in STUDENTS) != LABS_PASSED:
        problems.append(f"лабораторных: {sum(s.labs for s in STUDENTS)} ≠ {LABS_PASSED}")
    return problems
