# Replace Nested Conditional with Guard Clauses

Fowler (2018), ch. 10, p. 266. Formerly / aka: —. Inverse: —.

## When to use
- A conditional has one leg that is the normal behavior and other legs that are unusual
  or terminal cases (invalid input, missing data, "nothing to do").
- Nesting pushes the real work to the right, and the reader must keep every enclosing
  condition in mind to understand it.
- A `result` variable is assigned in several branches only to be returned at the end.

A guard clause marks a case as a side path: dispatch it and exit. An if/else presents two
paths as equally ordinary. Choose the shape that matches what the code means.

Do not use it when both legs are normal behavior: keep a plain if/else. Single-exit is a
style preference, so decide by readability.

## Mechanics
1. Pick the outermost condition that guards an unusual case and rewrite it as a guard
   clause: test the unusual case, return its result right away. If the condition guards
   the normal case instead, invert it first (apply De Morgan if needed, and simplify any
   leftover `!`) so that the unusual case becomes the early return.
2. Compile and run the tests.
3. Repeat for the next condition, working inward, one guard at a time.
4. When the guards no longer need the result variable, remove it and return values
   directly.
5. If several guards return the same value, merge them with
   Consolidate Conditional Expression ([consolidate-conditional-expression.md](consolidate-conditional-expression.md)).

## Example
Before: the fee is only computed when the order is neither a pickup nor empty, and is below the free-shipping threshold.

```csharp
public class Order
{
    public bool IsPickup { get; }
    public bool IsIsland { get; }
    public int ItemCount { get; }
    public int Zone { get; }
    public decimal Subtotal { get; }

    public Order(bool isPickup, bool isIsland, int itemCount, int zone, decimal subtotal)
    {
        IsPickup = isPickup;
        IsIsland = isIsland;
        ItemCount = itemCount;
        Zone = zone;
        Subtotal = subtotal;
    }
}

public class ShippingService
{
    public decimal ShippingFee(Order order)
    {
        decimal result;
        if (order.IsPickup)
        {
            result = 0m;
        }
        else
        {
            if (order.ItemCount == 0)
            {
                result = 0m;
            }
            else
            {
                if (order.Subtotal >= 100m)
                {
                    result = 0m;
                }
                else
                {
                    result = 7.5m + order.Zone * 1.5m;
                }
            }
        }
        return result;
    }
}
```

After the first guard (one step, tests run):

```csharp
public class ShippingService
{
    public decimal ShippingFee(Order order)
    {
        decimal result;
        if (order.IsPickup) return 0m;
        if (order.ItemCount == 0)
        {
            result = 0m;
        }
        else
        {
            if (order.Subtotal >= 100m) result = 0m;
            else result = 7.5m + order.Zone * 1.5m;
        }
        return result;
    }
}
```

Final, with the variable gone and the equal results consolidated:

```csharp
public class ShippingService
{
    public decimal ShippingFee(Order order)
    {
        if (order.IsPickup || order.ItemCount == 0 || order.Subtotal >= 100m) return 0m;
        return 7.5m + order.Zone * 1.5m;
    }
}
```

Reversing a condition: when an `||` test guards the normal path, invert it (De Morgan
turns the `||` into `&&`).

```csharp
// before
public class SurchargeRules
{
    public decimal RemoteSurcharge(Order order)
    {
        if (order.Zone >= 4 || order.IsIsland)
        {
            if (!order.IsPickup)
                return 12m;
        }
        return 0m;
    }
}
```

```csharp
// after
public class SurchargeRules
{
    public decimal RemoteSurcharge(Order order)
    {
        if (order.Zone < 4 && !order.IsIsland) return 0m;
        if (order.IsPickup) return 0m;
        return 12m;
    }
}
```

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Each guard keeps the original return value for its case, and the order of the guards
  matches the original order of evaluation (a guard that calls something with side effects
  must not move before another).
