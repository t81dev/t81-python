"""Core balanced ternary types."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import IntEnum


class Trit(IntEnum):
    """Balanced ternary digit."""

    NEG = -1
    ZERO = 0
    POS = 1


@dataclass(frozen=True)
class TritVector:
    """Immutable vector wrapper used by quantization and adapters."""

    values: tuple[Trit, ...]

    @classmethod
    def from_ints(cls, values: Iterable[int]) -> TritVector:
        return cls(values=tuple(Trit(v) for v in values))

    def to_ints(self) -> list[int]:
        return [int(v) for v in self.values]

    def __len__(self) -> int:
        return len(self.values)
