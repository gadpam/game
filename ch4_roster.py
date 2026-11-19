"""Заявка «Торпедо-2» для Главы 4 v2.

Сохраняет номера утверждённой Главы 3: Ветров остаётся №19, Шатский №16,
а будущий желаемый №8 никому не назначен. В Главе 4 Шатский возвращается
в основу, Ветров закономерно начинает матч в запасе.
"""
from __future__ import annotations

from ch3_roster import SQUAD_NUMBERS, VETROV_FUTURE_NUMBER, VETROV_NUMBER


STARTERS = (
    "ГРОМОВ",
    "САВЕЛЬЕВ",
    "АНДРЕЕВ",
    "КАРИМОВ",
    "ЛЕВЧУК",
    "ТКАЧЁВ",
    "ГОНЧАР",
    "НОВИК",
    "МАРЧЕНКО",
    "ДЕНИСОВ",
    "ШАТСКИЙ",
)

SUBS = (
    "БОБРОВ",
    "КИСЕЛЁВ",
    "МЕЛЬНИК",
    "КОВАЛЁВ",
    "РОМАНОВ",
    "ВЕТРОВ",
    "ЮРЧЕНКО",
)

assert len(STARTERS) == 11
assert len(SUBS) == 7
assert len(set(STARTERS + SUBS)) == 18
assert set(STARTERS + SUBS) == set(SQUAD_NUMBERS)
assert SQUAD_NUMBERS["ШАТСКИЙ"] == 16
assert SQUAD_NUMBERS["ВЕТРОВ"] == VETROV_NUMBER == 19
assert VETROV_FUTURE_NUMBER == 8
assert VETROV_FUTURE_NUMBER not in SQUAD_NUMBERS.values()
