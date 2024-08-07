from collections.abc import Callable, Sequence

import pytest

TOL = 1e-6
PMF = Sequence[float]
Gamble = Sequence[float]


def expectation(pmf: PMF, gamble: Gamble) -> float:
    return sum(p * g for p, g in zip(pmf, gamble))


def transform_expectations(
    transform: Callable[[Sequence[float]], float],  # sequence of expectations -> float
    credal_set: Sequence[PMF],
    gamble: Gamble,
) -> float:
    return transform([expectation(pmf, gamble) for pmf in credal_set])


def lower_expectation(credal_set: Sequence[PMF], gamble: Gamble) -> float:
    return transform_expectations(min, credal_set, gamble)


def upper_expectation(credal_set: Sequence[PMF], gamble: Gamble) -> float:
    return transform_expectations(max, credal_set, gamble)


def test_lower_upper_expectation() -> None:
    assert lower_expectation(
        credal_set=[[0.2, 0.2, 0.6], [0.1, 0.1, 0.8]],
        gamble=[5, 3, 1],
    ) == pytest.approx(1.6)
    assert lower_expectation(
        credal_set=[[0.2, 0.2, 0.6], [0.1, 0.1, 0.8]],
        gamble=[1, 4, 2],
    ) == pytest.approx(2.1)
    assert upper_expectation(
        credal_set=[[0.2, 0.2, 0.6], [0.1, 0.1, 0.8]],
        gamble=[1, 4, 2],
    ) == pytest.approx(2.2)
    assert lower_expectation(
        credal_set=[[0.2, 0.2, 0.6], [0.1, 0.1, 0.8]],
        gamble=[-1, -4, -2],
    ) == pytest.approx(-2.2)


def is_gamma_maxi_something(
    # something = gamble -> float (e.g. lower prevision, upper prevision, ...)
    something: Callable[[Gamble], float],
    gambles: Sequence[Gamble],
) -> Sequence[bool]:
    values = list(map(something, gambles))
    max_value = max(values)
    return [value + TOL >= max_value for value in values]


def is_gamma_maximin(
    credal_set: Sequence[PMF],
    gambles: Sequence[Gamble],
) -> Sequence[bool]:
    def something(gamble: Gamble) -> float:
        return lower_expectation(credal_set, gamble)

    return is_gamma_maxi_something(something, gambles)


def test_is_gamma_maximin() -> None:
    assert is_gamma_maximin(
        credal_set=[[0.5, 0.5], [0.8, 0.2]],
        gambles=[[440, 260], [420, 300], [370, 370]],
    ) == [False, False, True]


def is_gamma_maximax(
    credal_set: Sequence[PMF],
    gambles: Sequence[Gamble],
) -> Sequence[bool]:
    def something(gamble: Gamble) -> float:
        # we changed just the next line
        return upper_expectation(credal_set, gamble)

    return is_gamma_maxi_something(something, gambles)


def test_is_gamma_maximax() -> None:
    assert is_gamma_maximax(
        credal_set=[[0.5, 0.5], [0.8, 0.2]],
        gambles=[[440, 260], [420, 300], [370, 370]],
    ) == [True, False, False]


def hurwicz_expectation(
    beta: float,
    credal_set: Sequence[PMF],
    gamble: Gamble,
) -> float:
    def hurwicz(expectations: Sequence[float]) -> float:
        return beta * min(expectations) + (1 - beta) * max(expectations)

    return transform_expectations(hurwicz, credal_set, gamble)


def is_hurwicz(
    beta: float,
    credal_set: Sequence[PMF],
    gambles: Sequence[Gamble],
) -> Sequence[bool]:
    def something(gamble: Gamble) -> float:
        return hurwicz_expectation(beta, credal_set, gamble)

    return is_gamma_maxi_something(something, gambles)


def test_is_hurwicz() -> None:
    assert is_hurwicz(
        beta=0.5,
        credal_set=[[0.5, 0.5], [0.8, 0.2]],
        gambles=[[440, 260], [420, 300], [370, 370]],
    ) == [False, True, False]


# check dominance between two vectors, using min and max values
def interval_dominates(
    xs: Sequence[float],
    ys: Sequence[float],
) -> bool:
    return min(xs) > max(ys) + TOL


def is_maximal(
    # compares two vectors
    dominates: Callable[[Sequence[float], Sequence[float]], bool],
    # sequence of vectors
    xss: Sequence[Sequence[float]],
) -> Sequence[bool]:
    def is_not_dominated(xs: Sequence[float]) -> bool:
        return all(not dominates(ys, xs) for ys in xss)

    return [is_not_dominated(xs) for xs in xss]


def is_interval_maximal(
    credal_set: Sequence[PMF],
    gambles: Sequence[Gamble],
) -> Sequence[bool]:
    xss = [[expectation(pmf, gamble) for pmf in credal_set] for gamble in gambles]
    return is_maximal(interval_dominates, xss)


def test_is_interval_maximal() -> None:
    assert is_interval_maximal(
        credal_set=[[0.5, 0.5], [0.8, 0.2]],
        gambles=[[440, 260], [420, 300], [370, 370]],
    ) == [True, True, True]


# check dominance between two vectors, pointwise
def pointwise_dominates(
    xs: Sequence[float],
    ys: Sequence[float],
) -> bool:
    return all(x > y + TOL for x, y in zip(xs, ys))


def is_rbayes_maximal(
    credal_set: Sequence[PMF],
    gambles: Sequence[Gamble],
) -> Sequence[bool]:
    xss = [[expectation(pmf, gamble) for pmf in credal_set] for gamble in gambles]
    return is_maximal(pointwise_dominates, xss)


def test_is_rbayes_maximal() -> None:
    assert is_rbayes_maximal(
        credal_set=[[0.5, 0.5], [0.8, 0.2]],
        gambles=[[440, 260], [420, 300], [370, 370]],
    ) == [True, True, True]


def is_rbayes_admissible(
    credal_set: Sequence[PMF],
    gambles: Sequence[Gamble],
) -> Sequence[bool]:
    def arg_max(pmf: PMF) -> Sequence[bool]:
        xs = [expectation(pmf, gamble) for gamble in gambles]
        max_xs = max(xs)
        return [x + TOL >= max_xs for x in xs]

    def union(bss: Sequence[Sequence[bool]]) -> Sequence[bool]:
        return [any(bs) for bs in zip(*bss)]

    return union([arg_max(pmf) for pmf in credal_set])


def test_is_rbayes_admissible() -> None:
    assert is_rbayes_admissible(
        credal_set=[[0.5, 0.5], [0.8, 0.2]],
        gambles=[[440, 260], [420, 300], [370, 370]],
    ) == [True, False, True]
    assert is_rbayes_admissible(
        credal_set=[[0.5, 0.5], [0.65, 0.35], [0.8, 0.2]],
        gambles=[[440, 260], [420, 300], [370, 370]],
    ) == [True, True, True]


def combine(
    alpha: float,
    xs: Sequence[float],
    ys: Sequence[float],
) -> Sequence[float]:
    return [(1 - alpha) * x + alpha * y for x, y in zip(xs, ys)]


def test_combine() -> None:
    assert combine(0.5, [0.5, 0.5], [0.8, 0.2]) == pytest.approx([0.65, 0.35])


def test_extra() -> None:
    gambles = [[3, 9, 2], [4, 4, 4], [0, 3, 6], [6, 2, 1]]
    credal_set = [[0.4, 0.5, 0.1], [0.1, 0.8, 0.1], [0.6, 0.2, 0.2]]
    assert [[expectation(pmf, gamble) for pmf in credal_set] for gamble in gambles] == [
        pytest.approx([5.9, 7.7, 4]),
        pytest.approx([4, 4, 4]),
        pytest.approx([2.1, 3, 1.8]),
        pytest.approx([3.5, 2.3, 4.2]),
    ]
    assert [
        lower_expectation(credal_set, gamble) for gamble in gambles
    ] == pytest.approx([4, 4, 1.8, 2.3])
    assert [
        upper_expectation(credal_set, gamble) for gamble in gambles
    ] == pytest.approx([7.7, 4, 3, 4.2])
    assert [
        hurwicz_expectation(0.5, credal_set, gamble) for gamble in gambles
    ] == pytest.approx([5.85, 4, 2.4, 3.25])
    assert is_gamma_maximin(credal_set, gambles) == [True, True, False, False]
    assert is_gamma_maximax(credal_set, gambles) == [True, False, False, False]
    assert is_hurwicz(0.5, credal_set, gambles) == [True, False, False, False]
    assert is_interval_maximal(credal_set, gambles) == [True, True, False, True]
    assert is_rbayes_maximal(credal_set, gambles) == [True, True, False, True]
    assert is_rbayes_admissible(credal_set, gambles) == [True, False, False, True]


def test_extra_2() -> None:
    # from the 2007 paper
    # need convex combination for E-admissibility to be the same as robust Bayes
    pmfs: Sequence[Sequence[float]] = [[0.28, 0.72], [0.5, 0.5], [0.7, 0.3]]
    rvars: Sequence[Sequence[float]] = [
        [4, 0],
        [0, 4],
        [3, 2],
        [0.5, 3],
        [2.35, 2.35],
        [4.1, -0.3],
    ]
    assert is_gamma_maximin(pmfs, rvars) == [False, False, False, False, True, False]
    assert is_gamma_maximax(pmfs, rvars) == [False, True, False, False, False, False]
    assert is_rbayes_maximal(pmfs, rvars) == [True, True, True, False, True, False]
    assert is_interval_maximal(pmfs, rvars) == [True, True, True, False, True, True]
    assert is_rbayes_admissible(pmfs, rvars) == [True, True, True, False, False, False]
