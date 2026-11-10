# Substitute Algorithm

Fowler (2018), ch. 7, p. 195. Formerly / aka: —. Inverse: —.

## When to use
- You understand the problem better now and see a much simpler way to get the same result.
- A library, framework or language feature already provides what your own code does by hand.
- The behavior needs to change slightly, and swapping in a different algorithm first would make that change easy.

Do not use it on a big, tangled function as it stands. Break the function down first, so that what you replace is small and its behavior is easy to pin down.

## Mechanics
1. Isolate the code to replace so it fills a whole function by itself. Use Extract Function ([extract-function.md](extract-function.md)) and simplify further until the function is small.
2. Write tests that exercise only this function and capture its current behavior, including edge cases (empty input, no match, duplicates, boundary values).
3. Write the new algorithm next to the old one (for example under a temporary name), without removing the old one yet.
4. Run the compiler and any static analysis on the new code.
5. Run the tests against the new algorithm, and compare its output with the old one on the same inputs. If the results match, delete the old algorithm and give the function its final name. If they differ, keep the old version as the reference while you debug the new one.

## Example
Before: a hand-written accumulation that totals orders per customer and then scans for the biggest total.

```csharp
using System.Collections.Generic;

public record Order(string Customer, decimal Total);

public static class OrderStats
{
    public static string? TopCustomer(List<Order> orders)
    {
        var customers = new List<string>();
        var totals = new List<decimal>();
        foreach (var order in orders)
        {
            int index = customers.IndexOf(order.Customer);
            if (index < 0)
            {
                customers.Add(order.Customer);
                totals.Add(order.Total);
            }
            else
            {
                totals[index] += order.Total;
            }
        }
        if (customers.Count == 0) return null;
        int best = 0;
        for (int i = 1; i < customers.Count; i++)
        {
            if (totals[i] > totals[best]) best = i;
        }
        return customers[best];
    }
}
```

After: the same result, with grouping, summing and picking the maximum delegated to the library.

```csharp
using System.Collections.Generic;
using System.Linq;

public record Order(string Customer, decimal Total);

public static class OrderStats
{
    public static string? TopCustomer(List<Order> orders) =>
        orders
            .GroupBy(o => o.Customer)
            .Select(g => new { Customer = g.Key, Total = g.Sum(o => o.Total) })
            .MaxBy(x => x.Total)?.Customer;
}
```

Tests that pinned the old behavior (largest total wins, the first customer wins a tie, an empty list returns null) pass unchanged against the new body.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The function's tests ran against both algorithms with the same inputs before the old one was deleted.
