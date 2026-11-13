# Replace Loop with Pipeline

Fowler (2018), ch. 8, p. 231. Formerly / aka: —. Inverse: —.

## When to use
Smell: Loops. A loop that selects some items, converts them and gathers the results
reads better as a sequence of steps, each taking a collection and producing another, read
from top to bottom. Use it when the loop body mixes skipping, filtering, converting and
accumulating, or when it keeps flags only to skip or select elements.

Do not use it when the loop has real side effects per item that must happen in order, when
it exits early in a way no pipeline step expresses cleanly, or on a measured hot path where
the extra allocations matter.

## Mechanics
1. Introduce a new variable that holds the collection the loop iterates over (it can be a
   plain copy of the existing source) and make the loop iterate over it. Compile and test.
2. Take the first piece of behavior at the top of the loop (skipping items, a filter
   condition, a conversion) and remove it from the loop body. Add the matching operation to
   the expression that builds the new variable. Compile and test.
3. Repeat step 2 for each following piece of behavior, in order, testing after each one.
   Delete control variables that are no longer needed as they become dead.
4. When the loop does nothing but add items to an accumulator, remove the loop and assign
   the pipeline result to the accumulator instead. Compile and test.
5. Tidy up: inline the accumulator and the intermediate variable if that reads better,
   rename lambda parameters to say what they hold, and put one operation per line.

## Example
Before: the tracking codes of the first late shipments, up to a limit.

```csharp
using System;
using System.Collections.Generic;

public class Shipment
{
    public Shipment(string trackingCode, DateTime promisedBy, bool isDelivered)
    {
        TrackingCode = trackingCode;
        PromisedBy = promisedBy;
        IsDelivered = isDelivered;
    }

    public string TrackingCode { get; }
    public DateTime PromisedBy { get; }
    public bool IsDelivered { get; }
}

public class DelayReport
{
    public List<string> LateTrackingCodes(IEnumerable<Shipment> shipments, DateTime now, int limit)
    {
        var result = new List<string>();
        foreach (var shipment in shipments)
        {
            if (result.Count == limit) break;
            if (shipment.IsDelivered) continue;
            if (shipment.PromisedBy >= now) continue;
            result.Add(shipment.TrackingCode.ToUpperInvariant());
        }
        return result;
    }
}
```

After: the counter check and the `continue`s are gone, and each step is one line.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

public class DelayReport
{
    public List<string> LateTrackingCodes(IEnumerable<Shipment> shipments, DateTime now, int limit)
    {
        return shipments
            .Where(shipment => !shipment.IsDelivered)
            .Where(shipment => shipment.PromisedBy < now)
            .Select(shipment => shipment.TrackingCode.ToUpperInvariant())
            .Take(limit)
            .ToList();
    }
}
```

The limit counts results, not items read, so `Take` goes after the filters. Precondition: `limit >= 0`; for a negative limit the loop returned every match, while `Take` returns none.

## C# notes
- Use LINQ: `Where` for filter, `Select` for map, `Skip`/`Take` for slice, `ToList()` or
  `ToArray()` to produce the final collection.
- LINQ is lazy. Enumerate once, at the end of the pipeline, and do not hold a deferred query
  that is enumerated again later against changed or expensive-to-read data.
- Each step may allocate (delegates, iterators, intermediate arrays). On hot paths, measure
  before and after, and keep the loop if the cost shows up.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
