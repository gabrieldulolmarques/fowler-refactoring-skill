# Replace Derived Variable with Query

Fowler (2018), ch. 9, p. 248. Formerly / aka: —. Inverse: —.

## When to use
Smell: Mutable Data. A variable holds a value that is fully determined by other data
(a running total, a count, a cached sum), and every place that changes the source data also
has to remember to update the variable. Miss one update and the two disagree. Computing the
value when it is read removes that whole class of bugs and often states what the value means.

Do not apply it when the source data is immutable and the derived result can be immutable
too: building a new structure from it once is fine to keep. Also reconsider when the
calculation is expensive and read very often; measure before giving up the stored value.

## Mechanics
1. Find every place that assigns or updates the variable. If one variable mixes several
   sources (for example an initial value plus accumulated changes), apply Split Variable
   ([split-variable.md](split-variable.md)) first so each part has one meaning and one source.
2. Write a function or property that calculates the value from the source data.
3. At each read of the variable, assert that it equals the calculation (Introduce Assertion,
   [introduce-assertion.md](introduce-assertion.md)). If there is no single place to put the assertion, apply
   Encapsulate Variable ([encapsulate-variable.md](encapsulate-variable.md)) first.
4. Run the tests. If the assertion fails, the hypothesis is wrong or the split in step 1 is
   incomplete; fix that before continuing.
5. Replace each read of the variable with a call to the calculation.
6. Run the tests.
7. Remove the declaration and every update of the variable (Remove Dead Code,
   [remove-dead-code.md](remove-dead-code.md)), along with the assertion. Inline the calculation
   ([inline-function.md](inline-function.md)) if a separate helper is no longer useful.
8. Run the tests.

## Example
Before: `AmountPaid` is a second copy of information already held in `Payments`.

```csharp
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

public record Payment(decimal Amount);

public class Invoice
{
    private readonly List<Payment> _payments = new();
    private decimal _amountPaid;

    public Invoice(decimal total) => Total = total;

    public decimal Total { get; }
    public decimal AmountPaid => _amountPaid;
    public decimal Outstanding => Total - AmountPaid;

    public void Register(Payment payment)
    {
        _payments.Add(payment);
        _amountPaid += payment.Amount;
    }
}
```

Intermediate step: assert against the calculation, run the tests, then switch the reader.

```csharp
public decimal AmountPaid
{
    get
    {
        Debug.Assert(_amountPaid == CalculatedAmountPaid);
        return CalculatedAmountPaid;
    }
}

private decimal CalculatedAmountPaid => _payments.Sum(p => p.Amount);
```

After: the field and its update are gone.

```csharp
public class Invoice
{
    private readonly List<Payment> _payments = new();

    public Invoice(decimal total) => Total = total;

    public decimal Total { get; }
    public decimal AmountPaid => _payments.Sum(p => p.Amount);
    public decimal Outstanding => Total - AmountPaid;

    public void Register(Payment payment) => _payments.Add(payment);
}
```

If the field had started with a non-zero opening value, the assertion would fail. Split it
first into `_openingPaid` and an accumulator, and compute only the accumulator part.

## C# notes
- The calculation fits a computed read-only property (`=> ...`).
- `Debug.Assert` is removed from Release builds, so run the tests in Debug to exercise it.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
