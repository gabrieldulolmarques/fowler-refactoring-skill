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
5. If the body is tricky to fit, move it one statement at a time (see [move-statements-to-callers.md](move-statements-to-callers.md)) until the function is empty.
6. When no caller is left, delete the function.
7. If a step breaks the tests and the cause is not obvious, revert to the last green state and redo it in smaller steps.

## Example
Before: `IsLargeOrder` only wraps one comparison.

```csharp
public record Order(int Id, decimal Total);

public class Shipping
{
    public decimal Fee(Order order)
    {
        return IsLargeOrder(order) ? 0m : 9.90m;
    }

    private bool IsLargeOrder(Order o)
    {
        return o.Total > 500m;
    }
}
```

After: the call is replaced (parameter `o` becomes the argument `order`) and the helper is removed.

```csharp
public record Order(int Id, decimal Total);

public class Shipping
{
    public decimal Fee(Order order)
    {
        return order.Total > 500m ? 0m : 9.90m;
    }
}
```

A case that needs more fitting: the helper writes into an object the caller owns.

```csharp
using System.Linq;
using System.Text;

public record Cart(int[] ItemPrices);

public class CartSummary
{
    // Before
    public string BuildSummary(Cart cart)
    {
        var sb = new StringBuilder();
        AppendTotals(sb, cart);
        return sb.ToString();
    }

    private void AppendTotals(StringBuilder target, Cart source)
    {
        target.Append($"items: {source.ItemPrices.Length}; ");
        target.Append($"total: {source.ItemPrices.Sum()}");
    }
}

public class CartSummaryAfter
{
    // After
    public string BuildSummary(Cart cart)
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
