"""Amount input widgets with validation and auto-formatting to 2 decimal places.

Two variants are provided:

- :class:`AmountInput` — permissive, accepts any printable character including
  complex hledger amount expressions (e.g. ``-5 STCK @@ €200.00``).  Use this
  in posting rows where the user may enter commodity amounts.

- :class:`NumericAmountInput` — strict, accepts only a plain decimal number
  (digits, one decimal point, optional leading minus).  Use this wherever only
  a simple monetary value is expected (e.g. budget rule amounts).
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from textual.events import Blur
from textual.widgets import Input

from hledger_textual.widgets.constants import PASSTHROUGH_KEYS


class AmountInput(Input):
    """An Input that accepts any printable character and auto-formats on blur.

    Simple numeric values (e.g. "49", "-3.5") are reformatted to exactly
    2 decimal places when the field loses focus.  Complex hledger amount
    strings (e.g. "-5 STCK @@ €200.00") are left unchanged; validation
    happens at form-submission time.
    """

    _PASSTHROUGH_KEYS = PASSTHROUGH_KEYS

    def __init__(self, **kwargs) -> None:
        """Initialize with sensible defaults for an amount field."""
        kwargs.setdefault("placeholder", "0.00")
        super().__init__(**kwargs)

    @staticmethod
    def _format_amount(value: str) -> str:
        """Format a raw amount string to 2 decimal places.

        Args:
            value: The raw user input (e.g. "49", "-3.5", ".5").

        Returns:
            The value formatted with 2 decimal places when it is a plain
            number, or the original string unchanged for complex amounts.
        """
        stripped = value.strip()
        if not stripped:
            return ""
        try:
            d = Decimal(stripped)
            return f"{d:.2f}"
        except InvalidOperation:
            return stripped

    async def _on_key(self, event) -> None:
        """Allow all printable characters; pass navigation keys through."""
        key = event.key

        if key in self._PASSTHROUGH_KEYS:
            await super()._on_key(event)
            return

        # event.character is non-empty for printable characters.
        # Space is checked by name because some terminals emit it as a named
        # key with event.character=None rather than as the " " character.
        if event.character or key == "space":
            await super()._on_key(event)
            return

        event.prevent_default()
        event.stop()

    def _on_blur(self, event: Blur) -> None:
        """Auto-format to 2 decimal places when the field loses focus."""
        formatted = self._format_amount(self.value)
        if formatted != self.value:
            self.value = formatted


class NumericAmountInput(AmountInput):
    """An Input that only accepts plain decimal numbers and auto-formats on blur.

    Accepted characters are digits (0–9), a single decimal point, and a minus
    sign only at the start of the value.  Use this wherever a simple monetary
    value is expected (e.g. budget rule amounts) and hledger commodity syntax
    should not be permitted.
    """

    # Characters allowed in addition to digits.
    _ALLOWED_CHARS = frozenset({"-", "."})

    async def _on_key(self, event) -> None:
        """Allow digits, minus at start, and a single decimal point only."""
        key = event.key

        if key in self._PASSTHROUGH_KEYS:
            await super(AmountInput, self)._on_key(event)
            return

        char = event.character

        if char and (char.isdigit() or char in self._ALLOWED_CHARS):
            if char == "-":
                if self.cursor_position != 0 or "-" in self.value:
                    event.prevent_default()
                    event.stop()
                    return
            if char == ".":
                if "." in self.value:
                    event.prevent_default()
                    event.stop()
                    return
            await super(AmountInput, self)._on_key(event)
            return

        event.prevent_default()
        event.stop()
