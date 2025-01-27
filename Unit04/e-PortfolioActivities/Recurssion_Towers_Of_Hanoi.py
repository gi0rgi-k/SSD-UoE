def towers_of_hanoi(n, source, target, auxiliary):
    """
    Recursive function to solve Towers of Hanoi problem.
    Args:
    - n: Number of disks
    - source: The starting peg
    - target: The destination peg
    - auxiliary: The helper peg
    """
    if n == 1:
        print(f"Move disk 1 from {source} to {target}")
        return 1
    moves = towers_of_hanoi(n - 1, source, auxiliary, target)
    print(f"Move disk {n} from {source} to {target}")
    moves += 1
    moves += towers_of_hanoi(n - 1, auxiliary, target, source)
    return moves


def main():
    # Ask for the number of disks
    try:
        num_disks = int(input("Enter the number of disks: "))
        if num_disks <= 0:
            print("Number of disks must be greater than zero.")
            return

        print("\nSteps to solve the Towers of Hanoi:")
        total_moves = towers_of_hanoi(num_disks, 'A', 'C', 'B')
        print(f"\nTotal moves required: {total_moves}")
    except ValueError:
        print("Invalid input. Please enter a positive integer.")


if __name__ == "__main__":
    main()
