# Replace Error Code with Exception

https://refactoring.com/catalog/replaceErrorCodeWithException.html. Formerly / aka: —. Inverse: —.
Related: Replace Exception with Precheck ([replace-exception-with-precheck.md](replace-exception-with-precheck.md)).

## When to use
A function reports failure through its return value: a magic number, `null`, `false` or a
status object. Callers must check it after every call, and one that forgets lets the program
continue with bad state. Throwing moves the signal out of the normal return path and lets it
reach whichever layer can handle it.

Use it only for failures that are truly exceptional. If the condition is routine and callers
are expected to branch on it (a lookup that often finds nothing, input that is often invalid),
keep a return-based result or offer a precheck instead; see [replace-exception-with-precheck.md](replace-exception-with-precheck.md).

## Mechanics
1. Pick or create an exception type for the failure. Give it the information the error code
   carried (the code, a reason, the offending value).
2. Find every caller of the function and, at each call site, wrap the call so that the
   thrown exception is handled where the old code handled the error code. Do this before
   changing the function, keeping the old branch working. Compile and test.
3. In the function, replace the `return <error code>` with `throw new <Exception>(...)`.
   Compile and test.
4. In each caller, remove the now dead check of the error code. Compile and test.
5. If some callers cannot handle the exception, let it propagate to a layer that can; do not
   catch it only to turn it back into a code.
6. If the function's return type existed only to carry the code (an `int` status, a `bool`),
   simplify it, for example to `void`, as a separate step with [change-function-declaration.md](change-function-declaration.md).

## Example
Before: `Reserve` returns a code, and the caller must interpret it.

```csharp
using System;
using System.Collections.Generic;

public class Inventory
{
    private readonly Dictionary<string, int> _stock = new();

    public int Reserve(string sku, int quantity)
    {
        if (!_stock.TryGetValue(sku, out var available)) return -1; // unknown sku
        if (available < quantity) return -2;                        // not enough stock
        _stock[sku] = available - quantity;
        return 0;
    }
}

public class OrderService
{
    private readonly Inventory _inventory = new();

    public string Place(string sku, int quantity)
    {
        var result = _inventory.Reserve(sku, quantity);
        if (result == -1) return "unknown product";
        if (result == -2) return "out of stock";
        return "placed";
    }
}
```

After: failures are exceptions and the caller handles them where it chooses.

```csharp
using System;
using System.Collections.Generic;

public class ReservationException : Exception
{
    public ReservationException(string message) : base(message) { }
}

public class Inventory
{
    private readonly Dictionary<string, int> _stock = new();

    public void Reserve(string sku, int quantity)
    {
        if (!_stock.TryGetValue(sku, out var available))
            throw new ReservationException("unknown product");
        if (available < quantity)
            throw new ReservationException("out of stock");
        _stock[sku] = available - quantity;
    }
}

public class OrderService
{
    private readonly Inventory _inventory = new();

    public string Place(string sku, int quantity)
    {
        try
        {
            _inventory.Reserve(sku, quantity);
            return "placed";
        }
        catch (ReservationException e)
        {
            return e.Message;
        }
    }
}
```

## C# notes
- Do not use exceptions for expected control flow: they are slow compared with a branch and
  hide the normal paths of the program. Reserve them for failures the caller cannot reasonably
  avoid by checking first.
- Prefer a specific exception type (or a built-in one such as `ArgumentException` or
  `InvalidOperationException` where it fits) over a bare `Exception`, and catch the narrowest type.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Add a test per former error code that asserts the exception is thrown with the right data.
- Search for callers outside the solution (reflection, other assemblies) that still expect the code.
