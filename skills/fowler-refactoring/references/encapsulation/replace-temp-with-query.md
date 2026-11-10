# Replace Temp with Query

Fowler (2018), ch. 7, p. 178. Formerly / aka: —. Inverse: —.

## When to use
Smells: Long Function.

- A temp captures the result of an expression, and later code only reads it. Replacing it with a
  query gives the calculation a name and lets other methods reuse it.
- You are breaking up a long method and the temps force every extracted piece to take extra
  parameters. Once the temps are queries, the pieces can be extracted freely.
- The same value is computed the same way in several methods of a class.

Do not use it when:
- The variable is a snapshot of a value that changes later (an "old value" kept on purpose). The
  query would return a different result at the point of use.
- The variable is assigned in a way that cannot be gathered into one calculation.
- The code is outside a class and the query would need many parameters; the gain disappears.
- The calculation is expensive and used many times in a hot path; measure first or keep the temp.

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
public class Invoice
{
    private readonly int _hours;
    private readonly Consultant _consultant;

    public Invoice(int hours, Consultant consultant)
    {
        _hours = hours;
        _consultant = consultant;
    }

    public decimal Total()
    {
        var fees = _hours * _consultant.HourlyRate;
        var surchargeRate = 0.02m;
        if (fees > 5000m) surchargeRate = 0.05m;
        return fees + fees * surchargeRate;
    }
}

public record Consultant(decimal HourlyRate);
```

Step by step: `fees` is already assigned once, so extract its
right-hand side into `Fees`, inline the variable. Then extract `surchargeRate`, keeping both of its
assignments inside the new method, and inline it.

After:

```csharp
public class Invoice
{
    private readonly int _hours;
    private readonly Consultant _consultant;

    public Invoice(int hours, Consultant consultant)
    {
        _hours = hours;
        _consultant = consultant;
    }

    public decimal Total() => Fees + Fees * SurchargeRate;

    private decimal Fees => _hours * _consultant.HourlyRate;

    private decimal SurchargeRate => Fees > 5000m ? 0.05m : 0.02m;
}

public record Consultant(decimal HourlyRate);
```

Behavior is the same. `Fees` is now reusable by other methods, and `Total` no longer carries
temps that would block further extraction.

## C# notes
- A read-only property (`private decimal Fees => ...`) fits cheap, side-effect-free calculations.
- Keep expensive queries as methods (`ComputeFees()`), so the cost is visible at the call site.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The query returns the same value at every point where the temp was read (no state changes in
  between).
