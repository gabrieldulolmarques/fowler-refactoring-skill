# Split Phase

Fowler (2018), ch. 6, p. 154. Formerly / aka: —. Inverse: —.

## When to use

Smells: Divergent Change, Shotgun Surgery.

- A fragment does two different things in sequence, and the output of the first is the input of the second: parse then compute, compute then format, validate then execute.
- The inputs do not match the model the main logic needs, so the logic is cluttered with conversion work.
- If the first lines and the last lines touch unrelated variables and helper calls, they are probably two phases.
- Worth it when changes are coming to either concern. If the two parts will never change independently, a plain Extract Function may be enough.
- The phases can be functions, or larger modules. A phase may also be a small object (for example a transformer) instead of a function.

## Mechanics

1. Extract the code of the second phase into its own function ([extract-function.md](extract-function.md)). Pass whatever it needs as plain parameters for now, even if the list is long.
2. Compile and test.
3. Create the intermediate data structure and pass it to the extracted function as an extra parameter. At this point it can be empty.
4. Compile and test.
5. Go through the second-phase parameters one at a time. If the first phase produces or uses a parameter, store it as a field of the intermediate structure, read it from there in the second phase and drop the parameter. Compile and test after each move.
   - If a parameter should not be known to the second phase at all, compute the value it feeds in the first phase, store the result in a field, and move the line that fills it back to the caller ([move-statements-to-callers.md](../moving-features/move-statements-to-callers.md)).
   - Parameters used only by the second phase stay as parameters.
6. What remains in the original function is now the first phase. Turn it into a function of its own whose result is the intermediate structure ([extract-function.md](extract-function.md)), then compile and test. If the first phase grows helpers that share its inputs, it can be an object instead (a transformer) whose method returns the intermediate structure; see the variation below.
7. Optionally tidy: inline leftover temporaries in the orchestrating function so it reads as "run phase one, feed phase two".

## Example

Before: one method both gathers statistics and renders the text.

```csharp
using System.Collections.Generic;
using System.Text;

public record Order(string Id, decimal Amount);

public class ReportService
{
    public string OrdersReport(IReadOnlyList<Order> orders, string currencySymbol)
    {
        var count = orders.Count;
        decimal total = 0m;
        decimal largest = 0m;
        foreach (var order in orders)
        {
            total += order.Amount;
            if (order.Amount > largest) largest = order.Amount;
        }

        var sb = new StringBuilder();
        sb.AppendLine($"Orders: {count}");
        sb.AppendLine($"Total: {currencySymbol}{total:F2}");
        sb.AppendLine($"Largest: {currencySymbol}{largest:F2}");
        return sb.ToString();
    }
}
```

After: statistics and rendering are separate phases, linked by a `record`.

```csharp
using System.Collections.Generic;
using System.Text;

public record Order(string Id, decimal Amount);

public record OrderStats(int Count, decimal Total, decimal Largest);

public class ReportService
{
    public string OrdersReport(IReadOnlyList<Order> orders, string currencySymbol)
    {
        var stats = ComputeStats(orders);
        return Render(stats, currencySymbol);
    }

    private static OrderStats ComputeStats(IReadOnlyList<Order> orders)
    {
        decimal total = 0m;
        decimal largest = 0m;
        foreach (var order in orders)
        {
            total += order.Amount;
            if (order.Amount > largest) largest = order.Amount;
        }
        return new OrderStats(orders.Count, total, largest);
    }

    private static string Render(OrderStats stats, string currencySymbol)
    {
        var sb = new StringBuilder();
        sb.AppendLine($"Orders: {stats.Count}");
        sb.AppendLine($"Total: {currencySymbol}{stats.Total:F2}");
        sb.AppendLine($"Largest: {currencySymbol}{stats.Largest:F2}");
        return sb.ToString();
    }
}
```

Same output for the same input. Now a new output format touches only `Render`, and a new statistic touches `ComputeStats` plus the fields it feeds.

### Variation: the first phase as a transformer object

When the first phase needs several helpers over the same input, a small class keeps them together. The class takes the raw input, and one method returns the intermediate structure. `Render` does not change.

```csharp
using System.Collections.Generic;
using System.Linq;

public class OrderStatsCalculator
{
    private readonly IReadOnlyList<Order> _orders;

    public OrderStatsCalculator(IReadOnlyList<Order> orders) => _orders = orders;

    public OrderStats Run() => new(_orders.Count, Total(), Largest());

    private decimal Total() => _orders.Sum(o => o.Amount);

    private decimal Largest() => _orders.Aggregate(0m, (max, o) => o.Amount > max ? o.Amount : max);
}

public class ReportService
{
    public string OrdersReport(IReadOnlyList<Order> orders, string currencySymbol)
    {
        var stats = new OrderStatsCalculator(orders).Run();
        return Render(stats, currencySymbol);
    }

    // Render as above.
}
```

Same output as before, including an empty list and negative amounts (`Largest` still starts at `0`).

## C# notes

- The intermediate data structure is usually a `record` (or a `readonly record struct` for small, hot data). Immutability keeps the phases from reaching into each other's state.

## Verification

- Compiles and the tests pass after every step; one commit per refactoring.
- Behavior is unchanged: same output for the same input, including edge cases such as empty input.
- The second phase no longer reads anything that only the first phase should know; its parameters are the intermediate structure plus data it genuinely owns.
