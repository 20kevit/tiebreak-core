"""Ruleset model — inspectable metadata, frozen pins, reserved names."""
import pytest

from tiebreak_core import (
    CALCULATION_RULES_VERSION,
    SUPPORTED_RULESETS,
    RulesetInfo,
    available_rulesets,
    describe_ruleset,
    is_supported,
    UnsupportedRulesetError,
)


class TestRulesetMetadata:
    def test_legacy_is_implemented_and_frozen(self):
        info = describe_ruleset("legacy-0.1.0")
        assert isinstance(info, RulesetInfo)
        assert info.status == "implemented"
        assert info.id == CALCULATION_RULES_VERSION
        assert "buchholz" in info.criteria
        assert "direct_encounter" in info.criteria

    def test_fide_2026_is_reserved_not_implemented(self):
        info = describe_ruleset("fide-2026")
        assert info.status == "reserved"
        assert "2026" in info.fide_reference
        assert not is_supported("fide-2026")

    def test_unknown_ruleset_rejected(self):
        with pytest.raises(UnsupportedRulesetError):
            describe_ruleset("fide-1999")

    def test_available_lists_both(self):
        ids = {r.id for r in available_rulesets()}
        assert {"legacy-0.1.0", "fide-2026"} <= ids

    def test_supported_set_unchanged(self):
        assert SUPPORTED_RULESETS == ("legacy-0.1.0",)
        assert is_supported("legacy-0.1.0")

    def test_info_is_immutable(self):
        info = describe_ruleset("legacy-0.1.0")
        with pytest.raises(AttributeError):
            info.status = "reserved"
