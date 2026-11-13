# Encapsulate Variable

Fowler (2018), ch. 6, p. 132. Formerly / aka: Encapsulate Field, Self-Encapsulate Field. Inverse: —.

## When to use
Smells: Global Data, Mutable Data.

- Data is easy to reorganize only when access to it goes through functions: a function can be
  moved or renamed while an old one forwards to it, but raw data has to be repointed everywhere
  at once. Encapsulating first turns a hard data move into an easy function move.
- It also gives one place to add validation, side effects, logging or change tracking.
- The wider the scope of mutable data, the stronger the case. Data used inside a single small
  function rarely needs it.
- Immutable data needs it much less: nothing needs a hook before updates, and copies are safe.
- With legacy code, encapsulate a variable whenever you must add or change a reference to it,
  so coupling to it stops growing.
- Self-encapsulating a class's own fields (accessors even inside the class) is usually
  excessive. If a class is big enough to need it, split the class. It is still a useful step
  right before splitting one.

## Mechanics
1. Create a getter and a setter (or a property) that read and write the variable.
2. Build and run static checks.
3. Replace each direct read with the getter and each direct assignment with the setter, one
   reference at a time, running the tests after each.
4. Restrict the visibility of the variable (private, or a separate class) so the compiler
   reports any reference you missed and new direct access cannot appear.
   If visibility cannot be restricted, rename it to a deliberately conspicuous name (for
   example `_privateOnly_x`), build, and fix what breaks.
5. Run the tests.
6. Decide how deep the encapsulation goes (see below). If the value is a record, consider
   Encapsulate Record ([encapsulate-record.md](../encapsulation/encapsulate-record.md)).

### Encapsulating the value, not only the reference
The steps above control reassignment of the variable, not changes to the object it holds.
Options when callers should not mutate the shared object:
- Return a copy from the getter (common for lists). Callers can change their copy, but the
  shared data stays intact. Tests reveal code that relied on mutating the shared instance.
- Return a read-only wrapper or an immutable type, so mutation attempts fail visibly. This is
  often a good temporary measure to find all mutators, which you then remove or turn into
  explicit update methods, before switching the getter to a copy.
- Also copy in the setter when the source should not stay linked to the stored data.
- Copies and wrappers are one level deep. Nested structures need copies or wrappers at each
  level.

## Example
Before: a static field read and written from many classes.

```csharp
public class Billing
{
    public static decimal TaxRate = 0.18m;
}

public class InvoiceCalculator
{
    public decimal Total(decimal subtotal) => subtotal * (1 + Billing.TaxRate);
}

public class SettingsScreen
{
    public void Apply(decimal rate) => Billing.TaxRate = rate;
}
```

After: the field is renamed and private, and a property with the old name forwards to it.
Behavior is unchanged.

```csharp
public class Billing
{
    private static decimal _taxRate = 0.18m;

    public static decimal TaxRate
    {
        get => _taxRate;
        set => _taxRate = value;
    }
}

// Callers keep the same syntax: Billing.TaxRate and Billing.TaxRate = rate.
```

Follow-up change, not part of the refactoring because it changes behavior: with the setter
as the single entry point, validation can now be added in one place, and a negative rate
that used to be accepted now throws.

```csharp
using System;

public class Billing
{
    private static decimal _taxRate = 0.18m;

    public static decimal TaxRate
    {
        get => _taxRate;
        set
        {
            if (value < 0) throw new ArgumentOutOfRangeException(nameof(value));
            _taxRate = value;
        }
    }
}
```

Encapsulating the value: a shared list handed out as a copy.

```csharp
using System.Collections.Generic;
using System.Linq;

public class Customers
{
    private static List<string> _blocked = new();

    public static IReadOnlyList<string> Blocked => _blocked.ToList();
    public static void Block(string id) => _blocked.Add(id);
}
```

## C# notes
- A public field becomes a private field plus a property. In C#, switching a field to a
  property keeps the call syntax, but it breaks binary compatibility and anything that passes
  it by `ref`/`out` or relies on reflection by field name, so check those.
- A static field becomes a static property.
- A property sharing the field's name keeps call syntax, so step 3 has nothing to replace.
  Rename the field first (`_x`), add a property under the old name, then build. If callers
  must change (accessors as methods, or a renamed member), replace references one at a time
  with tests.
- Code that passes the member by `ref`/`out` no longer compiles against a property.
- A property of a struct type cannot be mutated in place (`Prop.X = 1` is a compile error);
  read it, change the copy and assign it back.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- No member outside the owning class references the field (build after making it private),
  and a search for the old name finds only the accessor.
