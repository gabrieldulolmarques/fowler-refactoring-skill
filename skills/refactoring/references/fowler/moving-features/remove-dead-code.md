# Remove Dead Code

Fowler (2018), ch. 8, p. 237. Formerly / aka: —. Inverse: —.

## When to use
Smells: Speculative Generality.
- A function, class, field, parameter or branch that nothing reaches any more. It costs
  nothing at run time, but every reader still has to work out what it does and why it can be
  ignored.
- Code left in comments, or behind a condition that can never be true. Version control
  already holds the old text, so the comment adds nothing.
- Do not delete code that is reachable in ways a text search cannot see until you have
  ruled those out (see C# notes). If you are unsure, find out first, or ask the owner.
- If you want to remember what was removed, a short note naming the revision is enough.
  Do not leave the code itself behind.

## Mechanics
1. If the code can be referenced from outside its own body (a whole function, class, field
   or parameter), search for uses: callers, overrides, implementations, and any place that
   names it as a string. For a public API, also consider callers outside the repository.
2. If something still uses it, it is not dead. Stop; this is not the refactoring to apply.
3. Delete the dead code. Build.
4. Run the tests.
5. Commit the removal on its own, so it can be reverted cleanly if a use turns up later.

## Example
Before:

```csharp
public class InvoiceService
{
    private const bool UseLegacyRounding = false;

    public decimal Total(Invoice invoice)
    {
        decimal total = invoice.Lines.Sum(l => l.Quantity * l.UnitPrice);

        if (UseLegacyRounding)
        {
            total = Math.Floor(total * 10m) / 10m;
        }

        // total = total - invoice.Discount;
        return Math.Round(total, 2);
    }

    private decimal ApplyLegacyFee(decimal total) => total * 1.02m;
}
```

After (a search found no caller of `ApplyLegacyFee`, and `UseLegacyRounding` is a constant
that is never true):

```csharp
public class InvoiceService
{
    public decimal Total(Invoice invoice)
    {
        decimal total = invoice.Lines.Sum(l => l.Quantity * l.UnitPrice);
        return Math.Round(total, 2);
    }
}
```

Behavior is the same: the removed branch never ran, the comment never executed, and the
private method had no callers.

## C# notes
- Code with no static callers may still be reached by reflection, dependency injection or
  serialization. Before deleting a type or member that looks unused, check for: types
  registered or resolved by a container (including by assembly scanning), members
  discovered by reflection or by naming convention, properties read or written by a
  serializer or ORM, event handlers wired by name, and members used only from configuration
  files or views.
- A `public` or `protected` member of a library can be used by projects you cannot see.
  Treat it as dead only if you know every consumer.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
