import re

# Regex for UK postcode validation
postcode_regex = r"^((([A-Z]{1,2}[0-9][0-9A-Z]?) ?[0-9][A-Z]{2})|(GIR ?0AA))$"

# Function to validate postcodes
def validate_postcode(postcode):
    if re.match(postcode_regex, postcode):
        return True
    return False

# List of test cases
postcodes = [
    "M1 1AA",     # Valid
    "M60 1NW",    # Valid
    "CR2 6XH",    # Valid
    "DN55 1PT",   # Valid
    "W1A 1HQ",    # Valid
    "EC1A 1BB",   # Valid
    "ST7 9HV",    # Invalid
]

# Validate and display results
for postcode in postcodes:
    result = validate_postcode(postcode)
    print(f"Postcode: {postcode} -> {'Valid' if result else 'Invalid'}")
