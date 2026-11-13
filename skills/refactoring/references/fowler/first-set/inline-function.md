# Inline Function

Fowler (2018), ch. 6, p. 115. Formerly / aka: Inline Method. Inverse: Extract Function
([extract-function.md](extract-function.md)).

## When to use
Smells: Lazy Element, Middle Man, Speculative Generality, Shotgun Surgery.

- The body says everything the name says, so the function adds a hop and no meaning.
- A chain of functions where each one just forwards to the next, and you lose track of where the work happens. Inline them, keep the hops that earn their place, drop the rest.
- One concern is spread over many small functions (Shotgun Surgery). Inline them, then re-extract along better lines.
- A set of functions split along the wrong lines. Inline them all into one function, then extract again with better boundaries.

Do not use it when the function is polymorphic (overridden), is recursive, has several return points that do not fit the caller, or when fitting the body into the caller is a large job. In those cases the cost is higher than the gain: leave the function alone.

## Mechanics
1. Check the function is not polymorphic: no subclass overrides it and it does not implement an interface member that other types also implement.
2. Find every caller (search the whole code base, not only the file).
3. Replace one call with the body, renaming parameters to the arguments in use and fitting local variables so they do not clash with the caller's.
4. Compile and run the tests after each replacement. The inlining need not be done all at once.
5. If the body is tricky to fit, move it one statement at a time (see [move-statements-to-callers.md](../moving-features/move-statements-to-callers.md)) until the function is empty.
6. When no caller is left, delete the function.
7. If a step breaks the tests and the cause is not obvious, revert to the last green state and redo it in smaller steps.

## Example
Before: `IsBulkOrder` only wraps one comparison.

```csharp
public class Cart
{
    public int Id { get; }
    public int Units { get; }

    public Cart(int id, int units)
    {
        Id = id;
        Units = units;
    }
}

public class Discounts
{
    public decimal UnitDiscount(Cart cart)
    {
        return IsBulkOrder(cart) ? 1.50m : 0m;
    }

    private bool IsBulkOrder(Cart c)
    {
        return c.Units >= 10;
    }
}
```

After: the call is replaced (parameter `c` becomes the argument `cart`) and the helper is removed.

```csharp
public class Discounts
{
    public decimal UnitDiscount(Cart cart)
    {
        return cart.Units >= 10 ? 1.50m : 0m;
    }
}
```

A case that needs more fitting: the helper writes into an object the caller owns.

```csharp
using System.Linq;
using System.Text;

public class PricedCart
{
    public decimal[] ItemPrices { get; }

    public PricedCart(decimal[] itemPrices) => ItemPrices = itemPrices;
}

public class CartSummary
{
    // Before
    public string BuildSummary(PricedCart cart)
    {
        var sb = new StringBuilder();
        AppendTotals(sb, cart);
        return sb.ToString();
    }

    private void AppendTotals(StringBuilder target, PricedCart source)
    {
        target.Append($"items: {source.ItemPrices.Length}; ");
        target.Append($"total: {source.ItemPrices.Sum()}");
    }
}

public class CartSummaryAfter
{
    // After
    public string BuildSummary(PricedCart cart)
    {
        var sb = new StringBuilder();
        sb.Append($"items: {cart.ItemPrices.Length}; ");
        sb.Append($"total: {cart.ItemPrices.Sum()}");
        return sb.ToString();
    }
}
```

## C# notes
- Do not inline a `virtual` or `override` method, or an interface implementation, without checking the other implementations: callers that go through the base type or interface still need the method.
- A method reached by reflection, dependency injection, serialization or an event subscription has callers that a text search will not find.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
