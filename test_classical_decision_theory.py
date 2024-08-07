from collections.abc import Sequence

from pytest import approx

PMF = Sequence[float]
Gamble = Sequence[float]


def expectation(pmf: PMF, gamble: Gamble) -> float:
    return sum(p * g for p, g in zip(pmf, gamble))


def test_expectation() -> None:
    assert expectation(pmf=[0.2, 0.2, 0.6], gamble=[5, 3, 1]) == approx(2.2)
