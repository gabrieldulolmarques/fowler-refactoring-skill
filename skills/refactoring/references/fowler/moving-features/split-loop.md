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
6. Consider Extract Function ([extract-function.md](../first-set/extract-function.md)) on each loop, and Replace Loop with Pipeline ([replace-loop-with-pipeline.md](replace-loop-with-pipeline.md)) where it reads better.

## Example
Before: one pass computes both the total weight and the latest delivery time.

```csharp
using System;
using System.Collections.Generic;

public class Delivery
{
    public Delivery(decimal weightKg, DateTime deliveredAt)
    {
        WeightKg = weightKg;
        DeliveredAt = deliveredAt;
    }

    public decimal WeightKg { get; }
    public DateTime DeliveredAt { get; }
}

public static class DeliveryReport
{
    public static string Summarize(IReadOnlyList<Delivery> deliveries)
    {
        decimal totalWeight = 0;
        DateTime latestDelivery = DateTime.MinValue;
        foreach (var delivery in deliveries)
        {
            totalWeight += delivery.WeightKg;
            if (delivery.DeliveredAt > latestDelivery) latestDelivery = delivery.DeliveredAt;
        }

        return $"weight: {totalWeight} kg, last delivery: {latestDelivery:yyyy-MM-dd}";
    }
}
```

After: one loop per concern, then each extracted into a function.

```csharp
using System;
using System.Collections.Generic;

public static class DeliveryReport
{
    public static string Summarize(IReadOnlyList<Delivery> deliveries)
    {
        return $"weight: {TotalWeight(deliveries)} kg, last delivery: {LatestDelivery(deliveries):yyyy-MM-dd}";
    }

    private static decimal TotalWeight(IReadOnlyList<Delivery> deliveries)
    {
        decimal totalWeight = 0;
        foreach (var delivery in deliveries)
        {
            totalWeight += delivery.WeightKg;
        }
        return totalWeight;
    }

    private static DateTime LatestDelivery(IReadOnlyList<Delivery> deliveries)
    {
        DateTime latestDelivery = DateTime.MinValue;
        foreach (var delivery in deliveries)
        {
            if (delivery.DeliveredAt > latestDelivery) latestDelivery = delivery.DeliveredAt;
        }
        return latestDelivery;
    }
}
```

Behavior is the same. Each function now has a single purpose and can later become a LINQ expression (`deliveries.Sum(d => d.WeightKg)`).

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Do not mix in an optimization or a pipeline rewrite in the same commit as the split.
