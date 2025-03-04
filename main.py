def add_numbers(num1, num2):
    return num1 + num2

def main():
    # Get input from the user
    num1 = float(input("Enter first number: "))
    num2 = float(input("Enter second number: "))

    # Call the function and display the result
    result = add_numbers(num1, num2)
    print("The sum is:", result)

# Standard Python convention to call the main function
if __name__ == "__main__":
    main()
