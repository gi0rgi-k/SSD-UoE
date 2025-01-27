def factorial(n: int) -> int:
    """
    Calculate the factorial of a non-negative integer.

    Args:
        n (int): The number to calculate the factorial for. Must be >= 0.

    Returns:
        int: The factorial of n.
    
    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("Input must be a non-negative integer.")
    if n == 0:
        return 1
    return n * factorial(n - 1)


if __name__ == "__main__":
    # Test the factorial function with a range of values
    test_values = [0, 1, 5, -1]
    for value in test_values:
        try:
            print(f"Factorial of {value}: {factorial(value)}")
        except ValueError as e:
            print(f"Error: {e}")
