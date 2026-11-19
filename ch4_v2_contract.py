"""Канонический вход и производственный контракт кандидата Главы 4 v2."""
from __future__ import annotations

from pathlib import Path


HOME_TEAM = "ВЕРЕСК"
AWAY_TEAM = "ТОРПЕДО-2"
HOME_SCORE = 1
AWAY_SCORE = 0
FINAL_SCORE = "ВЕРЕСК 1:0 ТОРПЕДО-2"

QUEST_RANK = "F−"
RECOVERY_GOAL = 3
DECISION_BEFORE = 26
DECISION_AFTER = 28
SUB_MINUTE = "65′"
MINUTES_PLAYED = 25
OFFICIAL_TACKLES = 2
MATCH_RATING = "6.6"

VETROV_NUMBER = 19
SHATSKY_NUMBER = 16

KIT_REFERENCE = Path("ch4/v2_veresk_kit_reference.jpg")
STADIUM_REFERENCE = Path("ch4/v2_03_veresk_stadium_establishing_src.jpg")

VERESK_KIT = {
    "shirt": "#49365C",
    "trim": "#D8CEB0",
    "shorts": "#D4C9A8",
    "socks": "#382542",
    "numbers": "#D8C27A",
    "goalkeeper": "#C98232",
}

STADIUM_FEATURES = (
    "red-brown running track",
    "asymmetrical concrete stands",
    "red-brick stair towers",
    "central steel canopy",
    "four lattice floodlight masts",
    "cold overcast late-November light",
)

assert QUEST_RANK == "F−"
assert DECISION_BEFORE < DECISION_AFTER <= 70
assert DECISION_AFTER - DECISION_BEFORE == 2
assert SUB_MINUTE == "65′" and MINUTES_PLAYED == 25
assert (HOME_SCORE, AWAY_SCORE) == (1, 0)
assert OFFICIAL_TACKLES < RECOVERY_GOAL
