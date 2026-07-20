def calculate_fibonacci(n):
    """Calculates and prints the first n Fibonacci numbers."""
    fib_numbers = []
    a, b = 0, 1
    for _ in range(n):
        fib_numbers.append(a)
        a, b = b, a + b
    print(f"The first {n} Fibonacci numbers are:")
    print(fib_numbers)

if __name__ == "__main__":
    n = 20
    calculate_fibonacci(n)