# Split Loop

Fowler (2018), ch. 8, p. 227. Formerly / aka: —. Inverse: —.

## When to use
Smells: Long Function.

- One loop does two or more unrelated jobs only because they can share a single pass over the data.
- You want to extract one of those jobs into its own function, but the loop would have to return several values or fill several variables.
- Anyone modifying one calculation has to understand all the others in the loop.

Do not decide against it only because the data is traversed twice. Clarity comes first; measure afterwards, and merge the loops back if the traversal is a proven bottleneck. A split loop is also often easier to optimize on its own. Leave the loop alone if the two computations really depend on each other (one reads what the other writes in the same pass).

## Mechanics
1. Make sure tests cover the loop's results.
2. Copy the loop, so the same traversal appears twice in sequence.
3. In each copy, remove the statements that belong to the other concern, especially anything with side effects (assignments, accumulation, calls that change state). Statements without side effects can stay for now.
4. Compile and run the tests.
5. Optionally use Slide Statements ([slide-statements.md](slide-statements.md)) to move each accumulator's declaration next to its own loop.
6. Consider Extract Function ([extract-function.md](extract-function.md)) on each loop, and Replace Loop with Pipeline ([replace-loop-with-pipeline.md](replace-loop-with-pipeline.md)) where it reads better.

## Example
Before: one pass computes both the total and the latest due date.

```csharp
using System;
using System.Collections.Generic;

public record Invoice(decimal Amount, DateTime DueDate);

public static class InvoiceReport
{
    public static string Summarize(IReadOnlyList<Invoice> invoices)
    {
        decimal total = 0;
        DateTime latestDue = DateTime.MinValue;
        foreach (var invoice in invoices)
        {
            total += invoice.Amount;
            if (invoice.DueDate > latestDue) latestDue = invoice.DueDate;
        }

        return $"total: {total}, latest due: {latestDue:yyyy-MM-dd}";
    }
}
```

After: one loop per concern, then each extracted into a function.

```csharp
using System;
using System.Collections.Generic;

public record Invoice(decimal Amount, DateTime DueDate);

public static class InvoiceReport
{
    public static string Summarize(IReadOnlyList<Invoice> invoices)
    {
        return $"total: {TotalAmount(invoices)}, latest due: {LatestDueDate(invoices):yyyy-MM-dd}";
    }

    private static decimal TotalAmount(IReadOnlyList<Invoice> invoices)
    {
        decimal total = 0;
        foreach (var invoice in invoices)
        {
            total += invoice.Amount;
        }
        return total;
    }

    private static DateTime LatestDueDate(IReadOnlyList<Invoice> invoices)
    {
        DateTime latestDue = DateTime.MinValue;
        foreach (var invoice in invoices)
        {
            if (invoice.DueDate > latestDue) latestDue = invoice.DueDate;
        }
        return latestDue;
    }
}
```

Behavior is the same. Each function now has a single purpose and can later become a LINQ expression (`invoices.Sum(i => i.Amount)`).

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Do not mix in an optimization or a pipeline rewrite in the same commit as the split.
