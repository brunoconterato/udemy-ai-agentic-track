N = 10000
total = 0.0
for i in range(1, N + 1):
    # The terms are 1/1 - 1/3 + 1/5 - 1/7 + ...
    # The denominator is 2*i - 1
    # The sign alternates: positive for odd indices (when viewed relative to the starting pattern)
    # Or based on i: if i is odd, sign is +, if i is even, sign is -
    sign = 1 if (i % 2 != 0) else -1
    term = sign / (2 * i - 1)
    total += term

result = total * 4
print(f"The calculated sum of the first {N} terms is: {total}")
print(f"Multiplying the total by 4 gives: {result}")