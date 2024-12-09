from collections.abc import Iterator
from dataclasses import dataclass, field
from fractions import Fraction
from random import Random
from typing import Any


# This module originally mostly comes from https://github.com/DRMacIver/junkdrawer
# but is provided here by the original author (David R. MacIver) under the normal
# ehrQL copyright and licensing.


class Coin:
    """Implements a weighted coin."""

    def __init__(self, positive, negative):
        """``positive`` and ``negative`` should be integers.
        This coin will return True with probability positive / (positive + negative),
        using O(1) expected bits.
        """
        validate_weight(positive, "positive")
        validate_weight(negative, "negative")
        if max(positive, negative) == 0:
            raise ValueError("At least one weight must be non-zero")
        self.trail = [(positive, negative)]

    @property
    def probability(self):
        return Fraction(self.trail[0][0]) / Fraction(sum(self.trail[0]))

    def toss(self, random):
        """Return True with the appopriate probability."""
        i = 0
        while True:
            if i == len(self.trail):
                a, b = self.trail[-1]
                assert a != b

                if a > b:
                    # p = a / (a + b) >= half. We've removed
                    # half from that so p_next = (p - 1/2) / (p - 1/2 + 1 - p)
                    # = 2p - 1. i.e. 2a / (a + b) - 1 = (2a - a - b) / (a + b)
                    # = (a - b) / (a + b). So a_next = a - b and b_next =
                    # (a + b - (a - b)) = 2b.
                    self.trail.append((a - b, 2 * b))
                else:
                    self.trail.append((2 * a, b - a))
            a, b = self.trail[i]
            assert a >= 0
            assert b >= 0
            if a == b:
                return bool(random.getrandbits(1))
            if random.getrandbits(1):
                return a > b
            i += 1


def validate_weight(weight, name):
    if weight < 0:
        raise ValueError(f"Expected non-negative value for {name} but got {weight}")


class VoseAliasSampler:
    """Samples values from a weighted distribution using Vose's algorithm for
    the Alias Method.

    See http://www.keithschwarz.com/darts-dice-coins/ for details.

    """

    def __init__(self, weights):
        assert any(weights)
        assert all(w >= 0 for w in weights)
        weights = list(map(Fraction, weights))

        n = len(weights)

        total = sum(weights)

        weights = tuple(w / total for w in weights)

        self._alias = [None] * len(weights)
        probabilities = [Fraction(-1)] * len(weights)

        self._size = total

        small = []
        large = []

        ps = [w * n for w in weights]

        for i, p in enumerate(ps):
            if p < 1:
                small.append(i)
            else:
                large.append(i)
        while small and large:
            lesser = small.pop()
            greater = large.pop()
            assert ps[greater] >= 1 >= ps[lesser]
            probabilities[lesser] = ps[lesser]
            self._alias[lesser] = greater
            ps[greater] = (ps[lesser] + ps[greater]) - 1
            if ps[greater] < 1:
                small.append(greater)
            else:
                large.append(greater)
        for q in [small, large]:
            while q:
                greater = q.pop()
                probabilities[greater] = Fraction(1)
                self._alias[greater] = greater

        assert None not in self._alias
        assert Fraction(-1) not in probabilities

        self.__coins = [
            Coin(x.numerator, x.denominator - x.numerator) for x in probabilities
        ]

    @property
    def _probabilities(self):
        return [coin.probability for coin in self.__coins]

    def sample(self, random):
        i = random.randrange(0, len(self.__coins))

        if self.__coins[i].toss(random):
            return i
        else:
            return self._alias[i]

    def __repr__(self):
        return f"VoseAliasSampler({list(zip(range(len(self._probabilities)), self._probabilities, self._alias))!r})"


class TreeSampler:
    """Implements an updatable sampler with integer weights.

    Behaves like a dict except the values must be integers >= 0
    and it has the additional sample() method which picks a random
    key with probability proportional to its weight.

    Updates and sampling are both log(n)
    """

    __slots__ = ("__items_to_indices", "__tree")

    def __init__(self, initial=()):
        self.__items_to_indices = {}
        # We store values in a binary tree unpacked as a list.
        # When modifying a weight we modify up to log(n) ancestors
        # in the tree to maintain an updated total weight.
        self.__tree = []

        if isinstance(initial, dict):
            initial = initial.items()
        for k, v in initial:
            self.__set_weight(k, v)

        for i in range(len(self.__tree) - 1, -1, -1):
            self.__update_node(i)

    def __getitem__(self, item) -> int:
        i = self.__items_to_indices[item]
        weight = self.__tree[i].weight
        if weight == 0:
            raise KeyError(item)
        return weight

    def __setitem__(self, item, weight):
        i = self.__set_weight(item, weight)
        self.__fix_tree(i)

    def __delitem__(self, item):
        self[item] = 0

    def __contains__(self, item) -> bool:
        try:
            i = self.__items_to_indices[item]
        except KeyError:
            return False
        return self.__tree[i].weight > 0

    def items(self) -> Iterator[tuple[int, int]]:
        for t in self.__tree:
            if t.weight > 0:
                yield (t.item, t.weight)

    def __iter__(self):
        for k, _ in self.items():
            yield k

    def __bool__(self):
        return len(self.__tree) > 0 and self.__tree[0].total_weight > 0

    def sample(self, random: Random):
        if not self.__tree or self.__tree[0].total_weight == 0:
            raise IndexError("Cannot sample from empty tree")
        i = 0
        while True:
            node = self.__tree[i]
            j1 = 2 * i + 1
            j2 = 2 * i + 2
            if j1 >= len(self.__tree):
                return node.item
            if node.weight > 0:
                if node.own_coin is None:
                    node.own_coin = Coin(node.weight, node.total_weight - node.weight)
                if node.own_coin.toss(random):
                    return node.item
            if j2 >= len(self.__tree):
                return self.__tree[j1].item
            if node.child_coin is None:
                node.child_coin = Coin(
                    self.__tree[j1].total_weight, self.__tree[j2].total_weight
                )
            if node.child_coin.toss(random):
                i = j1
            else:
                i = j2

    def __set_weight(self, item, weight):
        validate_weight(weight, "weight")
        try:
            i = self.__items_to_indices[item]
            self.__tree[i].weight = weight
        except KeyError:
            i = len(self.__items_to_indices)
            assert i == len(self.__tree)
            self.__items_to_indices[item] = i
            self.__tree.append(TreeNode(item, weight))
        return i

    def __update_node(self, i):
        node = self.__tree[i]
        node.total_weight = node.weight
        for j in (2 * i + 1, 2 * i + 2):
            if j < len(self.__tree):
                node.total_weight += self.__tree[j].total_weight
        node.own_coin = None
        node.child_coin = None

    def __fix_tree(self, i):
        while True:
            self.__update_node(i)
            if i == 0:
                break
            i = (i - 1) // 2


@dataclass
class TreeNode:
    item: int
    weight: Any
    total_weight: Any | None = field(default=None)

    own_coin: Coin | None = field(default=None)
    child_coin: Coin | None = field(default=None)
