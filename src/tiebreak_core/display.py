"""
Optional presentation metadata (Persian display names).

This module is OUTSIDE the calculation path. Calculators and ranking
never import it. chess-manager templates may use it for display, but
tiebreak-core correctness never depends on it.
"""
from typing import List, Tuple

TIEBREAK_NAMES_FA = {
    "buchholz": "بوخهلتس",
    "buchholz_cut1": "بوخهلتس کات ۱",
    "buchholz_cut2": "بوخهلتس کات ۲",
    "median_buchholz": "مدیان بوخهلتس",
    "median_buchholz_2": "مدیان بوخهلتس ۲",
    "sonneborn_berger": "زونبورن-برگر",
    "progressive": "پیشرونده",
    "wins": "تعداد برد",
    "wins_black": "برد با سیاه",
    "games_black": "بازی با سیاه",
    "aro": "میانگین ریتینگ حریفان",
    "koya": "کویا",
    "buchholz_sum": "مجموع بوخهلتس",
    "arpo": "ARPO",
    "sonneborn_berger_cut1": "زونبورن-برگر کات ۱",
    "progressive_cut1": "پیشرونده کات ۱",
    "aro_cut1": "میانگین ریتینگ حریفان کات ۱",
    "aob": "میانگین بوخهلتس حریفان",
    "fore_buchholz": "فور بوخهلتس",
    "won": "بردهای داخل صفحه",
    "rounds_elected": "راندهای انتخاب‌شده",
    "direct_encounter": "رویارویی مستقیم",
}

ALL_TIEBREAKS: List[Tuple[str, str]] = list(TIEBREAK_NAMES_FA.items())

# Legacy UI list (kept for chess-manager settings page compatibility).
ALL_TIEBREAKS_DISPLAY: List[Tuple[str, str]] = [
    ("buchholz", "بوخهلتس"),
    ("buchholz_cut1", "بوخهلتس کات ۱"),
    ("buchholz_cut2", "بوخهلتس کات ۲"),
    ("median_buchholz", "مدیان بوخهلتس"),
    ("sonneborn_berger", "زونبورن-برگر"),
    ("progressive", "پیشرونده"),
    ("wins", "تعداد برد"),
    ("wins_black", "برد با سیاه"),
    ("games_black", "بازی با سیاه"),
    ("aro", "میانگین ریتینگ حریفان"),
    ("koya", "کویا"),
    ("buchholz_sum", "مجموع بوخهلتس"),
    ("arpo", "ARPO"),
]
