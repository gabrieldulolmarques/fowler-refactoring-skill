# Substitute Algorithm

Fowler (2018), ch. 7, p. 195. Formerly / aka: —. Inverse: —.

## When to use
- You understand the problem better now and see a much simpler way to get the same result.
- A library, framework or language feature already provides what your own code does by hand.
- The behavior needs to change slightly, and swapping in a different algorithm first would make that change easy.

Do not use it on a big, tangled function as it stands. Break the function down first, so that what you replace is small and its behavior is easy to pin down.

## Mechanics
1. Isolate the code to replace so it fills a whole function by itself. Use Extract Function ([extract-function.md](../first-set/extract-function.md)) and simplify further until the function is small.
2. Write tests that exercise only this function and capture its current behavior, including edge cases (empty input, no match, duplicates, boundary values).
3. Write the new algorithm next to the old one (for example under a temporary name), without removing the old one yet.
4. Run the compiler and any static analysis on the new code.
5. Run the tests against the new algorithm, and compare its output with the old one on the same inputs. If the results match, delete the old algorithm and give the function its final name. If they differ, keep the old version as the reference while you debug the new one.

## Example
Before: a hand-written accumulation that totals charges per account and then scans for the biggest total.

```csharp
using System.Collections.Generic;

public class Charge
{
    public Charge(string account, decimal amount) { Account = account; Amount = amount; }
    public string Account { get; }
    public decimal Amount { get; }
}

public static class BillingStats
{
    public static string? TopAccount(List<Charge> charges)
    {
        var accounts = new List<string>();
        var totals = new List<decimal>();
        foreach (var charge in charges)
        {
            int index = accounts.IndexOf(charge.Account);
            if (index < 0)
            {
                accounts.Add(charge.Account);
                totals.Add(charge.Amount);
            }
            else
            {
                totals[index] += charge.Amount;
            }
        }
        if (accounts.Count == 0) return null;
        int best = 0;
        for (int i = 1; i < accounts.Count; i++)
        {
            if (totals[i] > totals[best]) best = i;
        }
        return accounts[best];
    }
}
```

After: the same result, with grouping, summing and ordering delegated to the library.

```csharp
using System.Collections.Generic;
using System.Linq;

public static class BillingStats
{
    public static string? TopAccount(List<Charge> charges) =>
        charges
            .GroupBy(c => c.Account)
            .Select(g => new { Account = g.Key, Total = g.Sum(c => c.Amount) })
            .OrderByDescending(x => x.Total)
            .FirstOrDefault()?.Account;
}
```

Tests that pinned the old behavior (largest total wins, the first account wins a tie, an empty list returns null) pass unchanged against the new body.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The function's tests ran against both algorithms with the same inputs before the old one was deleted.
