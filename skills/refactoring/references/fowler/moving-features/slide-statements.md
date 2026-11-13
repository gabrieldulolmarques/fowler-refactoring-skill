# Slide Statements

Fowler (2018), ch. 8, p. 223. Formerly / aka: formerly Consolidate Duplicate Conditional Fragments. Inverse: —.

## When to use
Smells: Duplicated Code, Mutable Data (and as a step inside Long Function).
- Lines that touch the same data are separated by lines that touch something else.
- A variable is declared far above its first use (declare it just before it is needed).
- You want to extract a group of lines but they are interleaved with other code. Sliding them together first makes the extraction possible.
- The same statements appear at the start or end of every branch of a conditional.

Not worth it if the slide cannot be made safe in small steps: do other preparation first (for example Split Variable on a reused variable) and come back.

## Mechanics
1. Choose the target position for the fragment (the statement or block you will move).
2. Check every statement between the fragment and the target for interference. Give up on this slide if any of these holds:
   - Moving up: the fragment would pass the declaration or assignment of something it reads.
   - Moving down: the fragment would pass a statement that reads something the fragment defines or changes.
   - The fragment would pass a statement that modifies something the fragment reads or writes.
   - The fragment modifies something that a statement in between reads.
   Statements without side effects can be reordered freely. Be careful with calls: only treat a call as side-effect free if you know it is.
3. Cut the fragment and paste it at the target.
4. Compile and run the tests.
5. If a test fails, undo and retry with a smaller step: slide over fewer statements, or move a smaller fragment. If that still fails, the slide may not be worth it yet.

Sliding out of a conditional: when the same statements end (or begin) every branch, and they do not depend on which branch ran in a way that changes behavior, remove them from each branch and put one copy after (or before) the conditional. Sliding into a conditional is the reverse and repeats the fragment in every branch.

## Example
Before: the discount lines are mixed with the surcharge lines, and `surcharge` is declared early.

```csharp
using System.Collections.Generic;
using System.Linq;

public class Courier
{
    public bool IsPartner { get; set; }
}

public class Parcel
{
    public decimal WeightKg { get; set; }
    public decimal RatePerKg { get; set; }
}

public class Shipment
{
    public Courier Courier { get; set; } = new();
    public List<Parcel> Parcels { get; set; } = new();
    public decimal DistanceKm { get; set; }
}

public class CostCalculator
{
    public decimal DeliveryCost(Shipment shipment)
    {
        decimal surcharge;
        var courier = shipment.Courier;
        decimal discount = 0m;
        var baseCost = shipment.Parcels.Sum(p => p.WeightKg * p.RatePerKg);
        surcharge = shipment.DistanceKm * 0.2m;
        if (courier.IsPartner) discount = baseCost * 0.1m;
        if (baseCost > 500m) surcharge = 0m;
        return baseCost - discount + surcharge;
    }
}
```

After: each declaration sits next to its use, and the discount lines are adjacent, ready for Extract Function.

```csharp
using System.Linq;

public class CostCalculator
{
    public decimal DeliveryCost(Shipment shipment)
    {
        var baseCost = shipment.Parcels.Sum(p => p.WeightKg * p.RatePerKg);

        var courier = shipment.Courier;
        decimal discount = 0m;
        if (courier.IsPartner) discount = baseCost * 0.1m;

        decimal surcharge = shipment.DistanceKm * 0.2m;
        if (baseCost > 500m) surcharge = 0m;

        return baseCost - discount + surcharge;
    }
}
```

Why it was safe: `baseCost` is declared before everything that reads it, and the surcharge lines read and write only `surcharge`, `shipment` and `baseCost`, none of which the discount lines change.

Conditional case, before and after (same behavior):

```csharp
using System.Collections.Generic;

public class Route
{
    public bool HasCapacity(Parcel parcel) => parcel.WeightKg <= 20m;
    public void Add(Parcel parcel) { }
    public void Defer(Parcel parcel) { }
}

public class Dispatcher
{
    private readonly List<string> _auditLog = new();

    public void AssignBefore(Route route, Parcel parcel, string trackingCode)
    {
        if (route.HasCapacity(parcel))
        {
            route.Add(parcel);
            _auditLog.Add(trackingCode);
        }
        else
        {
            route.Defer(parcel);
            _auditLog.Add(trackingCode);
        }
    }

    public void AssignAfter(Route route, Parcel parcel, string trackingCode)
    {
        if (route.HasCapacity(parcel))
            route.Add(parcel);
        else
            route.Defer(parcel);
        _auditLog.Add(trackingCode);
    }
}
```

This is only valid because the branches do not change what the audit entry observes.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- If coverage of the moved code is weak, add tests first: a slide that passes through shared mutable state is the kind of change tests catch best.
