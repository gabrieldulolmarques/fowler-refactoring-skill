# Chain Constructors

Kerievsky (2004), ch. 11, p. 340. Direction: —. Pattern: —.

## When to use
Smells: Duplicated Code.

- Two or more constructors repeat the same assignments. When someone adds a field and updates only one constructor, the others silently leave it unset.
- Let the more specific constructors call a more general one, until you reach a catch-all constructor that handles every case. It usually takes the most parameters.
- If a class has so many constructors that it is hard to use, consider [replace-constructors-with-creation-methods.md](../creation/replace-constructors-with-creation-methods.md), which itself relies on this refactoring.

## Mechanics
1. Find two constructors with duplicate code, and check whether one can call the other so the duplicated lines can be deleted from the caller. Make it call it. Compile and test.
2. Repeat for every constructor in the class, including those already changed, until duplication is as low as possible.
3. Re-check callers and reduce the visibility of any constructor that no longer needs to be public. Compile and test.

Prefer calling the catch-all constructor with explicit defaults rather than chaining sideways between narrow constructors, so there is one place where fields are assigned.

## Example
Before: three constructors each assign the fields themselves, and two repeat the same default due date.

```csharp
public class Payment
{
    private readonly decimal _amount;
    private readonly string _currency;
    private readonly DateOnly _dueDate;
    private readonly string? _reference;

    public Payment(decimal amount)
    {
        _amount = amount;
        _currency = "USD";
        _dueDate = DateOnly.FromDateTime(DateTime.Today).AddDays(30);
    }

    public Payment(decimal amount, string currency)
    {
        _amount = amount;
        _currency = currency;
        _dueDate = DateOnly.FromDateTime(DateTime.Today).AddDays(30);
    }

    public Payment(decimal amount, string currency, DateOnly dueDate, string? reference)
    {
        _amount = amount;
        _currency = currency;
        _dueDate = dueDate;
        _reference = reference;
    }
}
```

After: only the last constructor assigns fields; the others pass defaults to it.

```csharp
public class Payment
{
    private readonly decimal _amount;
    private readonly string _currency;
    private readonly DateOnly _dueDate;
    private readonly string? _reference;

    public Payment(decimal amount)
        : this(amount, "USD")
    {
    }

    public Payment(decimal amount, string currency)
        : this(amount, currency, DateOnly.FromDateTime(DateTime.Today).AddDays(30), null)
    {
    }

    public Payment(decimal amount, string currency, DateOnly dueDate, string? reference)
    {
        _amount = amount;
        _currency = currency;
        _dueDate = dueDate;
        _reference = reference;
    }
}
```

## C# notes
- C# chains with `: this(...)` before the constructor body, and `: base(...)` for the superclass. The chained call runs first, so a default expression cannot use instance members.
- Optional parameters are often the simpler alternative: one constructor, `Payment(decimal amount, string currency = "USD", DateOnly? dueDate = null, string? reference = null)`, with `dueDate ?? ...` inside. Use chaining instead when a default is computed, when two defaults must change together, or when the signature is part of a public API (adding an optional parameter changes call sites in other assemblies only after they recompile, while overloads stay binary compatible).
- On C# 12 and later, a class with a primary constructor makes the other constructors call `this(...)` on it by rule.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Every field is assigned in exactly one constructor, and each public constructor produces the same object as before for the same arguments.
