import sys

def calculate_series_sum(n):
    """
    Calculates the sum of the first n terms of the series 1 - 1/3 + 1/5 - 1/7 + ...
    The k-th term is (-1)^(k-1) / (2k - 1).
    """
    total_sum = 0.0
    for k in range(1, n + 1):
        # The denominator is 2k - 1
        denominator = 2 * k - 1
        # The sign is determined by (-1)^(k-1). If k is odd (k-1 is even), term is positive. If k is even (k-1 is odd), term is negative.
        sign = 1 if (k % 2 != 0) else -1
        term = sign / denominator
        total_sum += term
    return total_sum

N = 1000000
series_sum = calculate_series_sum(N)

# Multiply the total by 4
final_result = series_sum * 4

print(f"The sum of the first {N} terms of the series is: {series_sum}")
print(f"The final result (sum multiplied by 4) is: {final_result}")