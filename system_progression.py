"""Утверждённая кривая развития характеристик Системы (`curve-v1`).

Характеристики лежат в диапазоне 0..70. Система не показывает XP,
дробные очки или прогресс-бары: ``adaptation_units`` — внутренняя
редакторская величина, по которой определяется только целое изменение.

Кривая устроена ступенчато: каждые десять пунктов после 30 стоимость
следующего целого пункта удваивается. Поэтому один и тот же объём
подтверждённой работы даёт быстрый рост слабой характеристики и всё
меньший эффект по мере приближения к потолку.
"""

from __future__ import annotations

from dataclasses import dataclass

MIN_STAT = 0
MAX_STAT = 70

# (нижняя граница, верхняя граница, скрытая стоимость следующего +1)
PROGRESSION_TIERS = (
    (0, 29, 1),
    (30, 39, 2),
    (40, 49, 4),
    (50, 59, 8),
    (60, 69, 16),
)


@dataclass(frozen=True)
class ProgressResult:
    """Итог применения скрытых единиц адаптации к одной характеристике."""

    start: int
    value: int
    gained: int
    spent: int
    banked: int
    capped: bool


def _validate_value(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError('характеристика должна быть целым числом')
    if not MIN_STAT <= value <= MAX_STAT:
        raise ValueError(f'характеристика должна быть в диапазоне {MIN_STAT}..{MAX_STAT}')


def point_cost(current_value: int) -> int:
    """Вернуть скрытую стоимость перехода ``current_value -> +1``.

    Значение 70 является потолком и не имеет следующего пункта.
    """

    _validate_value(current_value)
    if current_value == MAX_STAT:
        raise ValueError('70 — потолок; следующий пункт не существует')
    for low, high, cost in PROGRESSION_TIERS:
        if low <= current_value <= high:
            return cost
    raise AssertionError('неполное покрытие шкалы прогрессии')


def effort_required(start: int, target: int) -> int:
    """Посчитать скрытую стоимость целого роста ``start -> target``."""

    _validate_value(start)
    _validate_value(target)
    if target < start:
        raise ValueError('эта модель считает только рост характеристики')
    return sum(point_cost(value) for value in range(start, target))


def apply_adaptation(value: int, adaptation_units: int, *, banked: int = 0) -> ProgressResult:
    """Применить внутреннюю адаптацию без вывода дробного прогресса в кадр.

    ``banked`` хранится только внутри логики Системы. В интерфейсе читатель
    видит либо целую пару значений (например, ``26 -> 28``), либо отсутствие
    изменения. На потолке неиспользованный остаток сгорает.
    """

    _validate_value(value)
    if isinstance(adaptation_units, bool) or not isinstance(adaptation_units, int):
        raise TypeError('единицы адаптации должны быть целым числом')
    if isinstance(banked, bool) or not isinstance(banked, int):
        raise TypeError('накопленный остаток должен быть целым числом')
    if adaptation_units < 0 or banked < 0:
        raise ValueError('единицы адаптации не могут быть отрицательными')
    if value == MAX_STAT:
        if banked:
            raise ValueError('на потолке скрытый остаток не хранится')
        return ProgressResult(value, value, 0, 0, 0, True)
    if banked >= point_cost(value):
        raise ValueError('banked должен быть меньше стоимости следующего пункта')

    start = value
    available = banked + adaptation_units
    spent = 0
    while value < MAX_STAT:
        cost = point_cost(value)
        if available < cost:
            break
        available -= cost
        spent += cost
        value += 1

    capped = value == MAX_STAT
    if capped:
        available = 0
    return ProgressResult(start, value, value - start, spent, available, capped)


# Авторские опорные примеры: менять только вместе с правилом прогрессии.
assert effort_required(28, 30) == 2
assert effort_required(45, 47) == 8
assert effort_required(60, 62) == 32
assert apply_adaptation(26, 2).value == 28
