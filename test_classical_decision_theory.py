from collections.abc import Callable, Sequence
from enum import Enum

import pytest

PMF = Sequence[float]
Gamble = Sequence[float]
Param = Enum("Param", ["LOW", "HIGH"])  # avg height in next hour
Data = Enum("Data", ["LOW", "HIGH"])  # avg height from last hour
Decision = Enum("Decision", ["BOAT", "NO_BOAT"])  # whether to send a boat
Strategy = Callable[[Data], Decision]  # function from data to decision


def expectation(pmf: PMF, gamble: Gamble) -> float:
    return sum(p * g for p, g in zip(pmf, gamble))


def test_expectation() -> None:
    assert expectation(pmf=[0.2, 0.2, 0.6], gamble=[5, 3, 1]) == pytest.approx(2.2)


def utility(d: Decision, x: Param) -> float:
    match d, x:
        case Decision.BOAT, Param.LOW:
            return 3
        case Decision.BOAT, Param.HIGH:
            return -1
        case _:  # all other cases
            return 0


def likelihood(y: Data, x: Param) -> float:
    # probability of data y given parameter x
    match y, x:
        case Data.LOW, Param.LOW:
            return 0.9
        case Data.HIGH, Param.LOW:
            return 0.1
        case Data.LOW, Param.HIGH:
            return 0.3
        case Data.HIGH, Param.HIGH:
            return 0.7
    assert False  # for mypy


def prior(x: Param):
    match x:
        case Param.LOW:
            return 0.4
        case Param.HIGH:
            return 0.6


def wald_expected_utility(strategy: Strategy, x: Param) -> float:
    pmf = [likelihood(y, x) for y in Data]
    gamble = [utility(strategy(y), x) for y in Data]
    return expectation(pmf=pmf, gamble=gamble)


def strategy_boat(y: Data) -> Decision:
    return Decision.BOAT


def strategy_no_boat(y: Data) -> Decision:
    return Decision.NO_BOAT


def strategy_boat_if_low(y: Data) -> Decision:
    return Decision.BOAT if y == Data.LOW else Decision.NO_BOAT


def strategy_boat_if_high(y: Data) -> Decision:
    return Decision.BOAT if y == Data.HIGH else Decision.NO_BOAT


strategies: Sequence[Strategy] = [
    strategy_boat,
    strategy_no_boat,
    strategy_boat_if_low,
    strategy_boat_if_high,
]


@pytest.mark.parametrize(
    "strategy,result",
    [
        (strategy_boat, [3, -1]),
        (strategy_no_boat, [0, 0]),
        (strategy_boat_if_low, [2.7, -0.3]),
        (strategy_boat_if_high, [0.3, -0.7]),
    ],
)
def test_wald(strategy: Strategy, result: Sequence[float]) -> None:
    assert [wald_expected_utility(strategy, x) for x in Param] == pytest.approx(result)


def posterior(x: Param, y: Data) -> float:
    return (
        likelihood(y, x) * prior(x) / sum(likelihood(y, x_) * prior(x_) for x_ in Param)
    )


def posterior_expected_utility(d: Decision, y: Data) -> float:
    pmf = [posterior(x, y) for x in Param]
    gamble = [utility(d, x) for x in Param]
    return expectation(pmf=pmf, gamble=gamble)


def test_bayes() -> None:
    assert posterior_expected_utility(Decision.BOAT, Data.LOW) == pytest.approx(5 / 3)
    assert posterior_expected_utility(Decision.NO_BOAT, Data.LOW) == pytest.approx(0)
    assert posterior_expected_utility(Decision.BOAT, Data.HIGH) == pytest.approx(
        -15 / 23
    )
    assert posterior_expected_utility(Decision.NO_BOAT, Data.HIGH) == pytest.approx(0)
