# CODE SOURCE: SOFTWARE ARCHITECTURE WITH PYTHON

"""
Module metricTest.py

Metric example - Module used as a testbed for static checkers.
This is a mix of different functions and classes performing various tasks.
"""
import random


def add_numbers(x: int, y: int) -> int:
    """Return the sum of two numbers."""
    return x + y


def find_optimal_route(start_time, expected_time, favorite_route='SBS1K', favorite_option='bus'):
    """
    Find the optimal route based on time and preferences.

    Args:
        start_time: The starting time.
        expected_time: The expected time to reach the destination.
        favorite_route: The default route.
        favorite_option: The default option (bus, car, etc.).

    Returns:
        The optimal route or a combination of routes.
    """
    delta_minutes = (expected_time - start_time).total_seconds() / 60.0

    if delta_minutes <= 30:
        return 'car'

    if 30 < delta_minutes < 45:
        return ('car', 'metro')

    if delta_minutes > 45:
        if delta_minutes < 60:
            return ('bus:335E', 'bus:connector')
        if delta_minutes > 80:
            return random.choice(('bus:330', 'bus:331', f'{favorite_option}:{favorite_route}'))
        if delta_minutes > 90:
            return f'{favorite_option}:{favorite_route}'


class BaseClass:
    """Base class example."""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def process(self):
        """Placeholder for a processing function."""
        pass

    def compute(self, x: int, y: int) -> int:
        """
        Compute a value based on inputs.

        Args:
            x: First input value.
            y: Second input value.

        Returns:
            Computed result.
        """
        if self.x > x:
            return self.x + self.y
        if x > self.x:
            return x + self.y


class DerivedClass(BaseClass):
    """Derived class example."""

    def __init__(self, x: int):
        super().__init__(x, 0)

    def process(self, x: int, y: int) -> int:
        """
        Override process to perform specific computations.

        Args:
            x: First input value.
            y: Second input value.

        Returns:
            Computed result.
        """
        if x > y:
            return x - y
        return x + y

    def compute(self, y: int) -> int:
        """
        Override compute with new logic.

        Args:
            y: Input value.

        Returns:
            Computed result.
        """
        if self.x > y:
            return self.x + y
        return y - self.x
