"""Example F — Article 16 policy.

The engines' defaults implement the FIDE-default unplayed-round
management (uncapped 2024 dummies / capped 2026 dummies, VUR-cut
preference, reapplied cuts). `resolve_policy` names that default and
records explicit §16.6 competition overrides as data — unknown or
incoherent overrides are rejected instead of silently applied.
"""
from tiebreak_core import (
    InvalidPlayerDataError,
    resolve_policy,
)


def main() -> None:
    default_24 = resolve_policy("fide-2024")
    default_26 = resolve_policy("fide-2026")
    rr_26 = resolve_policy("fide-2026", mode="round_robin")
    print("2024:", default_24)
    print("2026 swiss:", default_26)
    print("2026 RR:", rr_26)
    assert default_24.dummy_cap == "uncapped"
    assert default_26.dummy_cap == "capped"
    assert rr_26.forfeit_scope == "round_robin"

    # A §16.6 override is explicit data, not a scattered boolean.
    custom = resolve_policy("fide-2026", late_bye_value=0.0)
    assert custom.late_bye_value == 0.0
    assert custom.dummy_cap == "capped"  # everything else inherited

    try:
        resolve_policy("fide-2026", late_bye_value=0.3)
    except InvalidPlayerDataError as exc:
        print("rejected:", exc)


if __name__ == "__main__":
    main()
