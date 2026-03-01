"""Tests for date arithmetic utilities."""

from datetime import date

from hledger_textual.dateutil import next_month, prev_month


class TestPrevMonth:
    """Tests for prev_month."""

    def test_mid_year(self):
        """A mid-year date returns the first of the previous month."""
        assert prev_month(date(2026, 6, 15)) == date(2026, 5, 1)

    def test_january_wraps_to_december(self):
        """January wraps back to December of the previous year."""
        assert prev_month(date(2026, 1, 31)) == date(2025, 12, 1)

    def test_day_is_reset_to_first(self):
        """The day is always set to 1 regardless of input."""
        assert prev_month(date(2026, 3, 28)) == date(2026, 2, 1)

    def test_february_to_january(self):
        """February goes back to January of the same year."""
        assert prev_month(date(2026, 2, 1)) == date(2026, 1, 1)


class TestNextMonth:
    """Tests for next_month."""

    def test_mid_year(self):
        """A mid-year date returns the first of the next month."""
        assert next_month(date(2026, 6, 15)) == date(2026, 7, 1)

    def test_december_wraps_to_january(self):
        """December wraps forward to January of the next year."""
        assert next_month(date(2025, 12, 31)) == date(2026, 1, 1)

    def test_day_is_reset_to_first(self):
        """The day is always set to 1 regardless of input."""
        assert next_month(date(2026, 3, 28)) == date(2026, 4, 1)

    def test_november_to_december(self):
        """November advances to December of the same year."""
        assert next_month(date(2026, 11, 1)) == date(2026, 12, 1)


class TestRoundtrip:
    """Tests that prev_month and next_month are inverses."""

    def test_next_then_prev_returns_first_of_month(self):
        """next_month followed by prev_month returns the first of the original month."""
        d = date(2026, 7, 20)
        assert prev_month(next_month(d)) == date(2026, 7, 1)

    def test_prev_then_next_returns_first_of_month(self):
        """prev_month followed by next_month returns the first of the original month."""
        d = date(2026, 7, 20)
        assert next_month(prev_month(d)) == date(2026, 7, 1)

    def test_year_boundary_roundtrip(self):
        """Roundtrip across a year boundary is consistent."""
        d = date(2026, 1, 15)
        assert next_month(prev_month(d)) == date(2026, 1, 1)
