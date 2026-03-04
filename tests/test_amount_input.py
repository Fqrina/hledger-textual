"""Tests for AmountInput and NumericAmountInput keyboard handling and blur formatting."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Input

from hledger_textual.widgets.amount_input import AmountInput, NumericAmountInput


class _AmountApp(App):
    """Minimal app with an AmountInput for isolated widget testing."""

    def compose(self) -> ComposeResult:
        """Compose a single AmountInput and a second Input for blur testing."""
        yield AmountInput(id="amount")
        yield Input(id="other")


class TestAmountInputOnKey:
    """Tests for character filtering in AmountInput._on_key."""

    async def test_digit_is_inserted(self):
        """Digit characters pass through and are inserted into the value."""
        app = _AmountApp()
        async with app.run_test() as pilot:
            app.query_one("#amount").focus()
            await pilot.pause()
            await pilot.press("5")
            assert "5" in app.query_one("#amount", AmountInput).value

    async def test_letter_is_inserted(self):
        """Letter characters are accepted for commodity names (e.g. XEON)."""
        app = _AmountApp()
        async with app.run_test() as pilot:
            app.query_one("#amount").focus()
            await pilot.pause()
            await pilot.press("a")
            assert "a" in app.query_one("#amount", AmountInput).value

    async def test_uppercase_letter_is_inserted(self):
        """Uppercase letters are accepted for commodity names."""
        app = _AmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", AmountInput)
            inp.focus()
            await pilot.pause()
            await pilot.press("A")
            assert "A" in inp.value

    async def test_space_is_inserted(self):
        """Space is accepted to separate quantity from commodity."""
        app = _AmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", AmountInput)
            inp.focus()
            await pilot.pause()
            await pilot.press("5", "space", "X")
            assert " " in inp.value

    async def test_at_sign_is_inserted(self):
        """@ is accepted for cost annotations."""
        app = _AmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", AmountInput)
            inp.focus()
            await pilot.pause()
            await pilot.press("@")
            assert "@" in inp.value

    async def test_decimal_point_accepted(self):
        """A single decimal point is accepted after a digit."""
        app = _AmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", AmountInput)
            inp.focus()
            await pilot.pause()
            await pilot.press("5")
            await pilot.press(".")
            assert "." in inp.value

    async def test_minus_at_position_zero_accepted(self):
        """Minus sign at cursor position 0 is accepted."""
        app = _AmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", AmountInput)
            inp.focus()
            await pilot.pause()
            await pilot.press("-")
            assert inp.value.startswith("-")

    async def test_multiple_digits_inserted(self):
        """Multiple digit keypresses accumulate correctly."""
        app = _AmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", AmountInput)
            inp.focus()
            await pilot.pause()
            await pilot.press("1", "2", "3")
            assert inp.value == "123"

    async def test_negative_amount_with_digits(self):
        """Minus followed by digits produces a negative value."""
        app = _AmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", AmountInput)
            inp.focus()
            await pilot.pause()
            await pilot.press("-", "5", "0")
            assert inp.value == "-50"


class TestAmountInputOnBlur:
    """Tests for auto-formatting in AmountInput._on_blur."""

    async def test_integer_formatted_to_two_decimals(self):
        """An integer value is formatted to 2 decimal places when focus leaves."""
        app = _AmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", AmountInput)
            inp.focus()
            await pilot.pause()
            await pilot.press("4", "9")
            app.query_one("#other").focus()
            await pilot.pause()
            assert inp.value == "49.00"

    async def test_partial_decimal_gets_trailing_zero(self):
        """A single-decimal value gets a trailing zero on blur."""
        app = _AmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", AmountInput)
            inp.focus()
            await pilot.pause()
            await pilot.press("3", ".", "5")
            app.query_one("#other").focus()
            await pilot.pause()
            assert inp.value == "3.50"

    async def test_empty_value_stays_empty(self):
        """An empty field is not modified on blur."""
        app = _AmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", AmountInput)
            inp.focus()
            await pilot.pause()
            app.query_one("#other").focus()
            await pilot.pause()
            assert inp.value == ""

    async def test_already_formatted_value_unchanged(self):
        """A value already at 2 decimal places is not changed on blur."""
        app = _AmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", AmountInput)
            inp.focus()
            await pilot.pause()
            await pilot.press("1", "2", ".", "3", "4")
            app.query_one("#other").focus()
            await pilot.pause()
            assert inp.value == "12.34"

    async def test_complex_amount_not_reformatted_on_blur(self):
        """Complex hledger amount strings are not modified when focus leaves."""
        app = _AmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", AmountInput)
            inp.value = "-10 STCK @@ €200.00"
            inp.focus()
            await pilot.pause()
            app.query_one("#other").focus()
            await pilot.pause()
            assert inp.value == "-10 STCK @@ €200.00"


class _NumericAmountApp(App):
    """Minimal app with a NumericAmountInput for isolated widget testing."""

    def compose(self) -> ComposeResult:
        """Compose a single NumericAmountInput and a second Input for blur testing."""
        yield NumericAmountInput(id="amount")
        yield Input(id="other")


class TestNumericAmountInputOnKey:
    """Tests for character filtering in NumericAmountInput._on_key."""

    async def test_digit_is_inserted(self):
        """Digit characters pass through."""
        app = _NumericAmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", NumericAmountInput)
            inp.focus()
            await pilot.pause()
            await pilot.press("5")
            assert "5" in inp.value

    async def test_letter_is_blocked(self):
        """Letter characters are rejected."""
        app = _NumericAmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", NumericAmountInput)
            inp.focus()
            await pilot.pause()
            await pilot.press("a")
            assert inp.value == ""

    async def test_uppercase_letter_is_blocked(self):
        """Uppercase letters are rejected."""
        app = _NumericAmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", NumericAmountInput)
            inp.focus()
            await pilot.pause()
            await pilot.press("A")
            assert inp.value == ""

    async def test_space_is_blocked(self):
        """Space is rejected."""
        app = _NumericAmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", NumericAmountInput)
            inp.focus()
            await pilot.pause()
            await pilot.press("space")
            assert inp.value == ""

    async def test_at_sign_is_blocked(self):
        """@ is rejected."""
        app = _NumericAmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", NumericAmountInput)
            inp.focus()
            await pilot.pause()
            await pilot.press("@")
            assert inp.value == ""

    async def test_decimal_point_accepted(self):
        """A single decimal point is accepted."""
        app = _NumericAmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", NumericAmountInput)
            inp.focus()
            await pilot.pause()
            await pilot.press("5", ".")
            assert "." in inp.value

    async def test_second_decimal_point_blocked(self):
        """A second decimal point is rejected."""
        app = _NumericAmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", NumericAmountInput)
            inp.focus()
            await pilot.pause()
            await pilot.press("5", ".", "2", ".")
            assert inp.value.count(".") == 1

    async def test_minus_at_start_accepted(self):
        """Minus at position 0 is accepted."""
        app = _NumericAmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", NumericAmountInput)
            inp.focus()
            await pilot.pause()
            await pilot.press("-")
            assert inp.value.startswith("-")

    async def test_minus_after_digit_blocked(self):
        """Minus after a digit is rejected."""
        app = _NumericAmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", NumericAmountInput)
            inp.focus()
            await pilot.pause()
            await pilot.press("5", "-")
            assert "-" not in inp.value

    async def test_second_minus_blocked(self):
        """A second minus sign is rejected."""
        app = _NumericAmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", NumericAmountInput)
            inp.focus()
            await pilot.pause()
            await pilot.press("-", "-")
            assert inp.value.count("-") == 1

    async def test_blur_formats_to_two_decimals(self):
        """Numeric value is formatted to 2 decimal places on blur."""
        app = _NumericAmountApp()
        async with app.run_test() as pilot:
            inp = app.query_one("#amount", NumericAmountInput)
            inp.focus()
            await pilot.pause()
            await pilot.press("4", "9")
            app.query_one("#other").focus()
            await pilot.pause()
            assert inp.value == "49.00"
