# Replace Temp with Query

Fowler (2018), ch. 7, p. 178. Formerly / aka: —. Inverse: —.

## When to use
Smells: Long Function.

- A temp captures the result of an expression, and later code only reads it. Replacing it with a
  query gives the calculation a name and lets other methods reuse it.
- You are breaking up a long method and the temps force every extracted piece to take extra
  parameters. Once the temps are queries, the pieces can be extracted freely.
- The same value is computed the same way in several methods of a class.

**Beyond the book:** skip it when the variable is a snapshot of a value that changes later (an "old value" kept on purpose), since the query would return a different result at the point of use; when the variable is assigned in a way that cannot be gathered into one calculation; or when the code is outside a class and the query would need many parameters. If the calculation is expensive and used many times in a hot path, measure first or keep the temp.

## Mechanics
1. Make sure the value is settled before its first read and cannot differ on a later read of
   the same calculation.
2. If the variable is assigned more than once, restructure so it has a single assignment, or
   confirm that all the assignments will move into the query. C# has no read-only local, so
   confirm by reading the code or from compiler warnings. Use `const` only for compile-time
   values. Compile and test.
3. Extract the calculation of the variable into a new method or property. If the name you want
   collides with the variable, pick a provisional method name. Where several assignments
   build the value, the extracted method must contain all of them.
4. Make sure the new method has no side effects. If it has, apply Separate Query from Modifier
   ([separate-query-from-modifier.md](../refactoring-apis/separate-query-from-modifier.md)) first.
5. Compile and test.
6. Apply Inline Variable ([inline-variable.md](../first-set/inline-variable.md)) to remove the temp, replacing each read with a
   call to the query. Compile and test.
7. Repeat for the next temp.

## Example
Before:

```csharp
public class UsageInvoice
{
    private readonly int _units;
    private readonly PricingPlan _plan;

    public UsageInvoice(int units, PricingPlan plan)
    {
        _units = units;
        _plan = plan;
    }

    public decimal Total()
    {
        var charge = _units * _plan.UnitPrice;
        var discountRate = 0.05m;
        if (charge > 5000m) discountRate = 0.10m;
        return charge - charge * discountRate;
    }
}

public class PricingPlan
{
    public PricingPlan(decimal unitPrice) => UnitPrice = unitPrice;
    public decimal UnitPrice { get; }
}
```

Step by step: `charge` is already assigned once, so extract its
right-hand side into `Charge`, inline the variable. Then extract `discountRate`, keeping both of its
assignments inside the new method, and inline it.

After:

```csharp
public class UsageInvoice
{
    private readonly int _units;
    private readonly PricingPlan _plan;

    public UsageInvoice(int units, PricingPlan plan)
    {
        _units = units;
        _plan = plan;
    }

    public decimal Total() => Charge - Charge * DiscountRate;

    private decimal Charge => _units * _plan.UnitPrice;

    private decimal DiscountRate => Charge > 5000m ? 0.10m : 0.05m;
}
```

Behavior is the same. `Charge` is now reusable by other methods, and `Total` no longer carries
temps that would block further extraction.

## C# notes
- A read-only property (`private decimal Charge => ...`) fits cheap, side-effect-free calculations.
- Keep expensive queries as methods (`ComputeCharge()`), so the cost is visible at the call site.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The query returns the same value at every point where the temp was read (no state changes in
  between).
