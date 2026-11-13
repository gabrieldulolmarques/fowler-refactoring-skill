# Introduce Parameter Object

Fowler (2018), ch. 6, p. 140. Formerly / aka: —. Inverse: —.

## When to use
Smells: Data Clumps, Long Parameter List, Long Function, Primitive Obsession.

- The same group of values shows up as parameters in several functions, usually with the same
  names, or with slightly different names for the same idea.
- Naming the group makes the relationship between the values explicit, shortens signatures and
  makes every function reach the values the same way.
- Once the group is an object, behavior that works on it
  (validation, comparison, containment checks, formatting) has a natural place to live, and the
  object often turns into a real domain concept.
- Prefer Preserve Whole Object ([preserve-whole-object.md](../refactoring-apis/preserve-whole-object.md)) when the values are already
  fields of an existing object that the callee can simply receive.

## Mechanics
1. If no suitable structure exists, create one. Prefer a type that can later hold behavior, and
   make it immutable with value equality (a value object).
2. Run the tests.
3. Use Change Function Declaration ([change-function-declaration.md](change-function-declaration.md)) to add a parameter of
   the new type to the function. Where the language needs a value, pass `null` or a default at
   the callers for now.
4. Run the tests.
5. Update each caller to build and pass the right instance. Run the tests after each caller.
6. For each value in the group, one at a time: replace the uses of the original parameter inside
   the function with the matching member of the new object, remove that parameter from the
   signature and from every caller, and run the tests.
7. Look for behavior that can move into the new type (Move Function, [move-function.md](../moving-features/move-function.md))
   and for other places where the same group appears, and use the new type there too.

## Example
Before: the same pair of bounds travels together through two functions.

```csharp
using System.Collections.Generic;
using System.Linq;

public class CartLine
{
    public string Sku { get; }
    public decimal Price { get; }

    public CartLine(string sku, decimal price)
    {
        Sku = sku;
        Price = price;
    }
}

public class CartReport
{
    public decimal TotalBetween(IEnumerable<CartLine> lines, decimal min, decimal max) =>
        lines.Where(l => l.Price >= min && l.Price <= max).Sum(l => l.Price);

    public int CountBetween(IEnumerable<CartLine> lines, decimal min, decimal max) =>
        lines.Count(l => l.Price >= min && l.Price <= max);
}

// caller
// var total = report.TotalBetween(lines, band.Min, band.Max);
// var count = report.CountBetween(lines, band.Min, band.Max);
```

After: the pair is a `PriceRange`, and the containment check moved into it.

```csharp
using System.Collections.Generic;
using System.Linq;

public class PriceRange
{
    public decimal Min { get; }
    public decimal Max { get; }

    public PriceRange(decimal min, decimal max)
    {
        Min = min;
        Max = max;
    }

    public bool Contains(decimal value) => value >= Min && value <= Max;
}

public class CartReport
{
    public decimal TotalBetween(IEnumerable<CartLine> lines, PriceRange range) =>
        lines.Where(l => range.Contains(l.Price)).Sum(l => l.Price);

    public int CountBetween(IEnumerable<CartLine> lines, PriceRange range) =>
        lines.Count(l => range.Contains(l.Price));
}

// caller
// var range = new PriceRange(band.Min, band.Max);
// var total = report.TotalBetween(lines, range);
// var count = report.CountBetween(lines, range);
```

Behavior is unchanged. The intermediate states (both the old parameters and the new one in the
signature) compiled and passed the tests at each step.

## C# notes
- The new type can be a class, a `record` or a `record struct`. A `record` gives value equality
  and immutability (`init` or positional properties) for free, which suits a value object (C# 9+; on Unity it needs an `IsExternalInit` shim).

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- No caller still passes the old individual values, and no function reads them from anywhere
  other than the new object.
