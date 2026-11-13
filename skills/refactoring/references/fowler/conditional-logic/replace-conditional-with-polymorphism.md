# Replace Conditional with Polymorphism

Fowler (2018), ch. 10, p. 272. Formerly / aka: —. Inverse: —.

## When to use
Smells: Repeated Switches, Primitive Obsession, Long Function.

- Several functions switch on the same type code (account kind, document type, plan). Each new kind forces you to edit every switch. Moving each kind into a class puts all of its behavior in one place and removes the duplication.
- One case is the normal path and a few others tweak it. Keep the normal path in the base class and give each tweak its own subclass.

A plain `if`/`switch` is usually enough. Use this when the same conditional is repeated or hard to follow and the cases are real kinds.

## Mechanics
1. If no classes exist for the cases, create them: a base class (or interface) with one subclass per case, plus a factory function that returns the right instance.
2. Change callers to get the object from the factory instead of constructing it or passing the type code around. Compile and test.
3. If the conditional is not already a self-contained method, isolate it with [extract-function.md](../first-set/extract-function.md), then place that method on the base class.
4. Pick one case. Add an override in its subclass containing that branch's logic, adjusted to use the subclass's own members. Optionally make the matching branch in the base method throw, so a test fails if it is still reached. Compile and test.
5. Repeat step 4 for every branch, testing after each.
6. Decide what the base method does. Keep the default branch as the base implementation, or, if the base class should never be used alone, make the method `abstract`. If the base stays concrete, the factory must return the base class for unknown values; if it is abstract, the factory must reject them.

**Beyond the book:** if the logic is spread over free functions, group them first with [combine-functions-into-class.md](../first-set/combine-functions-into-class.md). When the last branch has moved, remove the now-empty `switch` and, if nothing else uses it, the type code; keep the code as a property until its last reader is gone. For a base-and-variant case, you may need to extract the varying part of a large method first, so the subclass can override only that part and call `base` for the rest; name the extracted pieces after what they mean, not after the case.

## Example
Before: two methods switch on the same shipping method.

```csharp
using System;

public enum ShippingMethod { Standard, Express, Pickup }

public class Shipment
{
    public ShippingMethod Method { get; }
    public decimal WeightKg { get; }

    public Shipment(ShippingMethod method, decimal weightKg)
    {
        Method = method;
        WeightKg = weightKg;
    }

    public decimal Cost()
    {
        switch (Method)
        {
            case ShippingMethod.Standard: return 4m + WeightKg * 1.2m;
            case ShippingMethod.Express: return WeightKg > 20m ? 60m : 12m + WeightKg * 2.5m;
            case ShippingMethod.Pickup: return 0m;
            default: throw new InvalidOperationException();
        }
    }

    public int EstimatedDays()
    {
        switch (Method)
        {
            case ShippingMethod.Standard: return 5;
            case ShippingMethod.Express: return 2;
            case ShippingMethod.Pickup: return 1;
            default: throw new InvalidOperationException();
        }
    }
}
```

After: one class per method, created by a factory; the switches are gone. An unknown method now fails when the object is created instead of when a method is called (same exception type). In this example nothing reads `Method` any more, so it was removed. In real code keep it until its last reader is gone.

```csharp
using System;

public enum ShippingMethod { Standard, Express, Pickup }

public abstract class Shipment
{
    public decimal WeightKg { get; }

    protected Shipment(decimal weightKg) => WeightKg = weightKg;

    public static Shipment Create(ShippingMethod method, decimal weightKg) => method switch
    {
        ShippingMethod.Standard => new StandardShipment(weightKg),
        ShippingMethod.Express => new ExpressShipment(weightKg),
        ShippingMethod.Pickup => new PickupShipment(weightKg),
        _ => throw new InvalidOperationException()
    };

    public abstract decimal Cost();
    public abstract int EstimatedDays();
}

public class StandardShipment : Shipment
{
    public StandardShipment(decimal weightKg) : base(weightKg) { }
    public override decimal Cost() => 4m + WeightKg * 1.2m;
    public override int EstimatedDays() => 5;
}

public class ExpressShipment : Shipment
{
    public ExpressShipment(decimal weightKg) : base(weightKg) { }
    public override decimal Cost() => WeightKg > 20m ? 60m : 12m + WeightKg * 2.5m;
    public override int EstimatedDays() => 2;
}

public class PickupShipment : Shipment
{
    public PickupShipment(decimal weightKg) : base(weightKg) { }
    public override decimal Cost() => 0m;
    public override int EstimatedDays() => 1;
}
```

Variant of the same idea, base plus one variant: `ParcelQuote` holds the normal rules, and `OversizedParcelQuote` overrides only the part that differs. The factory picks the subclass. Before, it was a single method: `Total(weightKg, oversized) => weightKg * 2m + (oversized ? 15m : 0m)`.

```csharp
public class ParcelQuote
{
    protected readonly decimal WeightKg;
    public ParcelQuote(decimal weightKg) => WeightKg = weightKg;

    public static ParcelQuote Create(decimal weightKg, bool oversized) =>
        oversized ? new OversizedParcelQuote(weightKg) : new ParcelQuote(weightKg);

    public decimal Total() => WeightKg * 2m + Surcharge();
    protected virtual decimal Surcharge() => 0m;
}

public class OversizedParcelQuote : ParcelQuote
{
    public OversizedParcelQuote(decimal weightKg) : base(weightKg) { }
    protected override decimal Surcharge() => base.Surcharge() + 15m;
}
```

## C# notes
- A `switch` on a type code becomes `abstract` or `virtual` members, or an interface, depending on whether the cases share code.
- The factory is the one place that still switches on the code. Keep it small and cover it with a test for every value, including the unknown one.
- If the type code is persisted or serialized, keep it as data and map it in the factory.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Each moved branch has a test that fails if the override is removed (if you used the optional throw in step 4, the base method throws until the last branch is moved).
