# Move Function

Fowler (2018), ch. 8, p. 198. Formerly / aka: Move Method. Inverse: —.

## When to use
Smells: Feature Envy, Divergent Change, Shotgun Surgery, Temporary Field, Message Chains, Insider Trading, Alternative Classes with Different Interfaces, Data Class.

- The function reads or writes members of another type more than members of the type it lives in.
- Its callers, or the place you need to call it from next, are in a different context.
- A helper nested inside another function (or buried in a private section) has value on its own.
- A behavior is about to vary by the other type (for example, per kind of customer), so it belongs there.

When the choice of home is unclear, the choice usually matters little. Put the function in the best candidate and move it again once you learn more. If no existing context fits a group of functions, create one first (Combine Functions into Class, Extract Class).

## Mechanics
1. List everything the function uses in its current context: other functions, fields, constants. Decide whether any of them should move too. If a called function should move, move it first; start the cluster with the function that depends least on the others. When some helpers are called from this one function and nowhere else, it can be simpler to inline them, move the single function, and extract the helpers again once it is in its new place.
2. Check whether the function is polymorphic (virtual, override, interface implementation, or a member of a hierarchy). If so, take the other declarations into account before moving.
3. Copy the function into the target context, with a temporary name if that helps tell the two apart. Adjust it to fit: replace uses of source members with the target's own members, and pass what is still needed from the source as parameters (a value, or the source object itself).
4. Compile. Fix undefined or inaccessible symbols in the copy (visibility, missing parameters, missing helpers). The original is untouched, so behavior is unchanged.
5. Decide how the source context reaches the target: a field, a property, a parameter, or a lookup.
6. Turn the original into a thin forwarder: its body becomes a single call that hands the work to the moved copy.
7. Compile and run the tests. This is the step that proves the moved function works in its new home.
8. Decide whether to keep the delegating function. If callers can reach the target directly, inline the source function ([inline-function.md](inline-function.md)) and update the callers; otherwise it can stay.
9. Give the target function its final name, now that it lives in its new context ([change-function-declaration.md](change-function-declaration.md)), and move any helper functions that only it used.

## Example
Before: `Order` computes a shipping fee from data that mostly belongs to `Customer`.

```csharp
public class Customer
{
    public string Region { get; init; } = "";
    public bool IsMember { get; init; }
}

public class Order
{
    public Customer Customer { get; init; } = new();
    public decimal Subtotal { get; init; }

    public decimal Total => Subtotal + ShippingFee();

    public decimal ShippingFee()
    {
        if (Customer.IsMember) return 0m;
        return Customer.Region == "domestic" ? 5m : 20m;
    }
}
```

Step 3 to 7: copy the function to `Customer` (the order is not needed, so no parameter), then delegate from `Order`.

```csharp
public class Customer
{
    public string Region { get; init; } = "";
    public bool IsMember { get; init; }

    public decimal ShippingFee()
    {
        if (IsMember) return 0m;
        return Region == "domestic" ? 5m : 20m;
    }
}

public class Order
{
    public Customer Customer { get; init; } = new();
    public decimal Subtotal { get; init; }

    public decimal Total => Subtotal + ShippingFee();

    public decimal ShippingFee() => Customer.ShippingFee();
}
```

Step 8: only `Total` calls it, so inline the delegating function.

```csharp
public class Order
{
    public Customer Customer { get; init; } = new();
    public decimal Subtotal { get; init; }

    public decimal Total => Subtotal + Customer.ShippingFee();
}
```

If the moved function later needs more from the order (for example the subtotal for a free-shipping threshold), pass the order instead of single values: `Customer.ShippingFee(this)`.

## C# notes
- The target can be another class, a static class, or an extension method. An extension method suits a type you cannot edit, but it can only use public members.
- Moving a `virtual`, `override` or interface-implementing method changes the contract for other implementations; check them first.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
