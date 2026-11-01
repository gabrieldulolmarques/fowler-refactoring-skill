# Preserve Whole Object

Fowler (2018), ch. 11, p. 319. Formerly / aka: —. Inverse: —.

## When to use
Smells: Long Function, Long Parameter List, Data Clumps.

- Callers read two or more values from one object and pass them on. Pass the object instead.
- The signature stops changing when the function later needs another field of that object.
- Several callers repeat the same logic over the unpacked parts. That logic often belongs on the whole object (Feature Envy; see [move-function.md](move-function.md)).
- Common right after Introduce Parameter Object ([introduce-parameter-object.md](introduce-parameter-object.md)): hunt down the remaining call sites that still unpack the data.
- If several callers only ever use the same subset of the object's members, consider [extract-class.md](extract-class.md).
- An object calling another object with several of its own values can pass `this` instead.

Do not use it when the callee must not depend on the whole object's type, typically because they live in different modules or layers. Then keep the primitive parameters, or pass a smaller object.

## Mechanics
1. Declare a new, empty method with the signature you want (the whole object as parameter). Give it a unique, easy-to-search temporary name.
2. Make its body call the old method, mapping from the whole object to the old parameters.
3. Compile (static checks).
4. Change callers one at a time to use the new method, compiling and testing after each. Locals that only fed the old arguments may become dead; remove them ([remove-dead-code.md](remove-dead-code.md)).
5. When no caller of the old method is left, inline the old method into the new one ([inline-function.md](inline-function.md)).
6. Rename the new method to the original name, and update its callers (the unique temporary name lets a plain text search find every call site to update).

Variation: if you prefer to build the new method from other refactorings, use [extract-variable.md](extract-variable.md) on the call and on the object expression at one caller, then [extract-function.md](extract-function.md) on the call, and [move-function.md](move-function.md) if it belongs on the callee's class. Continue from step 4.

## Example
Before:

```csharp
public record DateRange(DateOnly Start, DateOnly End);

public class Invoice
{
    public DateRange Period { get; init; } = new(default, default);
}

public class BillingCalendar
{
    private readonly DateRange _open = new(new DateOnly(2025, 1, 1), new DateOnly(2025, 12, 31));

    public bool Covers(DateOnly start, DateOnly end) =>
        start >= _open.Start && end <= _open.End;
}

public class InvoiceAuditor
{
    public void Audit(Invoice invoice, BillingCalendar calendar, List<string> findings)
    {
        var from = invoice.Period.Start;
        var to = invoice.Period.End;
        if (!calendar.Covers(from, to))
            findings.Add("billing period is not covered by the calendar");
    }
}
```

Intermediate (steps 1 to 2; the new method delegates to the old one):

```csharp
public bool xxNewCovers(DateRange period) => Covers(period.Start, period.End);
```

After (callers migrated, old method inlined, temporary name removed):

```csharp
public class BillingCalendar
{
    private readonly DateRange _open = new(new DateOnly(2025, 1, 1), new DateOnly(2025, 12, 31));

    public bool Covers(DateRange period) =>
        period.Start >= _open.Start && period.End <= _open.End;
}

public class InvoiceAuditor
{
    public void Audit(Invoice invoice, BillingCalendar calendar, List<string> findings)
    {
        if (!calendar.Covers(invoice.Period))
            findings.Add("billing period is not covered by the calendar");
    }
}
```

Behavior is the same; the `from` and `to` locals are gone.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- After step 5, a search for the old method's name finds no remaining caller. After step 6, a search for the temporary prefix (`xx`) finds nothing.
