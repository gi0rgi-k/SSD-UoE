import os

def list_directory():
    """Lists the contents of the current directory."""
    print("\n".join(os.listdir()))

def add_numbers():
    """Prompts user to add two numbers."""
    try:
        num1 = float(input("Enter the first number: "))
        num2 = float(input("Enter the second number: "))
        print(f"Result: {num1 + num2}")
    except ValueError:
        print("Invalid input. Please enter valid numbers.")

def show_help():
    """Displays the list of available commands."""
    print("Available commands:")
    print("LIST - List contents of the current directory")
    print("ADD - Add two numbers together")
    print("HELP - Display the list of commands")
    print("EXIT - Exit the shell")

def shell():
    """Command Line Interface (CLI) implementation."""
    print("Welcome to the Python CLI Shell. Type HELP for a list of commands.")
    while True:
        command = input("Enter a command: ").strip().upper()
        if command == "LIST":
            list_directory()
        elif command == "ADD":
            add_numbers()
        elif command == "HELP":
            show_help()
        elif command == "EXIT":
            print("Exiting the shell. Goodbye!")
            break
        else:
            print("Invalid command. Type HELP for the list of commands.")

if __name__ == "__main__":
    shell()
