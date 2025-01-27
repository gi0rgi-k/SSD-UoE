def add_numbers_secure():
    """Prompts user to add two numbers with secure validation."""
    while True:
        try:
            num1 = input("Enter the first number: ").strip()
            if not num1.isdigit():
                raise ValueError("Invalid input. Must be a number.")
            num2 = input("Enter the second number: ").strip()
            if not num2.isdigit():
                raise ValueError("Invalid input. Must be a number.")
            num1, num2 = float(num1), float(num2)
            print(f"Result: {num1 + num2}")
            break
        except ValueError as e:
            print(e)
