# Inline Variable

Fowler (2018), ch. 6, p. 123. Formerly / aka: Inline Temp. Inverse: Extract Variable
([extract-variable.md](extract-variable.md)).

## When to use
- The variable's name adds nothing beyond what the expression already says, so it is only
  an extra line to read.
- The variable stands between you and another refactoring: for example, it is read inside a
  block you want to extract or move, and keeping it forces an extra parameter or return value.
- Do not inline when the name explains a non-obvious expression, or when the expression is
  expensive and the variable is read many times. In those cases the variable earns its place.

## Mechanics
1. Check that the right-hand side has no side effects. If it has, stop.
2. As an extra precaution, check that nothing between the assignment and the reads can change
   what the right-hand side evaluates to. If something can, stop.
3. Confirm the variable is assigned exactly once. In C# this check is manual: a `const` local
   needs a compile-time constant, so the compiler cannot confirm single assignment for other
   values. Search the method for other assignments, including `out`, `ref`, `+=` and `++`.
   If the value is a constant, a temporary `const` makes the compiler check it; for a field,
   `readonly` does the same. Run the tests.
4. Replace the first read of the variable with the right-hand side. Build and test.
5. Repeat for each remaining read, testing as you go.
6. Delete the declaration and the assignment. Build and test.

## Example
Before:

```csharp
public record Invoice(DateTime DueDate);

public class CollectionsPolicy
{
    public bool IsSeriouslyOverdue(Invoice invoice, DateTime today)
    {
        int daysLate = (today - invoice.DueDate).Days;
        return daysLate > 30;
    }
}
```

After:

```csharp
public record Invoice(DateTime DueDate);

public class CollectionsPolicy
{
    public bool IsSeriouslyOverdue(Invoice invoice, DateTime today)
    {
        return (today - invoice.DueDate).Days > 30;
    }
}
```

Behavior is the same: the expression is evaluated once, at the same point, with no side effects.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- After the last read is replaced, the variable has no references left; the compiler fails if
  the declaration was deleted too early.
