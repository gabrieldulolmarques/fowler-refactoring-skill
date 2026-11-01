# Replace Query with Parameter

Fowler (2018), ch. 11, p. 327. Formerly / aka: -. Inverse: Replace Parameter with Query
([replace-parameter-with-query.md](replace-parameter-with-query.md)).

## When to use
- A function reads something from outside its own scope (a global, a singleton, a static member, an
  element of a module you plan to move away) and you want the function to stop depending on it.
- The function is hard to test or reason about because its result changes with hidden state. Moving
  the lookup to a parameter makes it return the same result for the same arguments (referential
  transparency), so the logic can sit in a pure core wrapped by code that handles I/O and shared
  state.
- Trade-off: the caller now has to find and pass the value, so call sites get heavier and
  parameter lists longer. If many callers repeat the same lookup, or the dependency is harmless,
  keep the query inside (the inverse refactoring). Decide by where the responsibility belongs; the
  choice is reversible.

## Mechanics
1. Apply Extract Variable ([extract-variable.md](extract-variable.md)) to the query expression, so it sits in one
   local variable apart from the rest of the body. Compile and test.
2. Apply Extract Function ([extract-function.md](extract-function.md)) to everything except the line that performs
   the query. The new function takes the variable as a parameter. Give it a temporary, easily
   searchable name. Compile and test.
3. Apply Inline Variable ([inline-variable.md](inline-variable.md)) to the variable from step 1, so the original
   function just calls the new one with the query expression as the argument. Compile and test.
4. Apply Inline Function ([inline-function.md](inline-function.md)) to the original function, so every caller now
   calls the new function and passes the query itself. Compile and test.
5. Rename the new function to the original name, using the searchable temporary name to find
   every use. Compile and test.

## Example
Before: the method reads a static clock.

```csharp
public class Invoice
{
    private readonly decimal _amount;
    private readonly DateTime _dueDate;
    private readonly decimal _dailyPenaltyRate;

    public Invoice(decimal amount, DateTime dueDate, decimal dailyPenaltyRate)
    {
        _amount = amount;
        _dueDate = dueDate;
        _dailyPenaltyRate = dailyPenaltyRate;
    }

    public decimal Penalty()
    {
        var daysLate = (DateTime.Today - _dueDate).Days;
        return daysLate > 0 ? _amount * _dailyPenaltyRate * daysLate : 0m;
    }
}

// caller
var penalty = invoice.Penalty();
```

After: the caller supplies the date, and `Penalty` depends only on its arguments and the
immutable fields.

```csharp
public class Invoice
{
    private readonly decimal _amount;
    private readonly DateTime _dueDate;
    private readonly decimal _dailyPenaltyRate;

    public Invoice(decimal amount, DateTime dueDate, decimal dailyPenaltyRate)
    {
        _amount = amount;
        _dueDate = dueDate;
        _dailyPenaltyRate = dailyPenaltyRate;
    }

    public decimal Penalty(DateTime today)
    {
        var daysLate = (today - _dueDate).Days;
        return daysLate > 0 ? _amount * _dailyPenaltyRate * daysLate : 0m;
    }
}

// caller
var penalty = invoice.Penalty(DateTime.Today);
```

A test can now pass any date and get a repeatable result.

## C# notes
- Useful to remove a dependency on a static or singleton (`DateTime.Today`, a static configuration
  class, a service locator) and make the code testable.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Every caller passes the value the old internal query returned, so behavior is unchanged.
