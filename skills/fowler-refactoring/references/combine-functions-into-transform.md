# Combine Functions into Transform

Fowler (2018), ch. 6, p. 149. Formerly / aka: —. Inverse: —. Alternative:
Combine Functions into Class ([combine-functions-into-class.md](combine-functions-into-class.md)).

## When to use
Smells: Shotgun Surgery, Mutable Data.

- Several clients derive values (a total, a charge, a status) from the same source record, and
  the formulas are repeated or live in helpers nobody knows about.
- You want one place to look at and change every derivation: the transform.
- The source data is read-only in practice (a report, a view model, an input that is only read).

Do not use it when clients modify the source after the transform. The derived fields are
stored in the copy, so a later change to the source leaves them stale. In that case use
Combine Functions into Class, where the derived values are computed on demand.

Choose between transform and class mostly by the style the codebase already uses, with that
one exception.

## Mechanics
1. Create a transform function that takes the source record and returns a copy with the same
   values. Make the copy deep if the record holds mutable nested data.
2. Add a test that the transform does not change the record passed in.
3. Pick one derivation. If its logic is not yet a function, apply Extract Function first.
4. Move the body into the transform so it fills a new field on the copy. Move any helper the
   body needs too, or make it reachable from the transform.
5. Make one client call the transform and read the new field instead of calculating it.
6. Compile and test.
7. Repeat steps 3 to 6 for each remaining derivation and each remaining client. A derivation
   that builds on another one should read the other's field.
8. When no client calls the old helper any more, delete it or nest it in the transform. Inline
   the variables that now only copy a field.

## Example
Before: two places compute the same subtotal.

```csharp
using System;

public record Order(string Customer, int Units, decimal UnitPrice, int Year);

public static class Reports
{
    private static decimal TaxFreeAllowance(int year) => year >= 2024 ? 100m : 50m;

    public static decimal InvoiceTotal(Order order)
    {
        var subtotal = order.Units * order.UnitPrice;
        return subtotal;
    }

    public static decimal TaxDue(Order order)
    {
        var subtotal = order.Units * order.UnitPrice;
        var taxable = Math.Max(0, subtotal - TaxFreeAllowance(order.Year));
        return taxable * 0.2m;
    }
}
```

After: one transform holds both derivations; clients read fields.

```csharp
using System;

public record Order(string Customer, int Units, decimal UnitPrice, int Year);

public record EnrichedOrder(
    string Customer, int Units, decimal UnitPrice, int Year,
    decimal Subtotal, decimal TaxableAmount);

public static class OrderEnricher
{
    private static decimal TaxFreeAllowance(int year) => year >= 2024 ? 100m : 50m;

    public static EnrichedOrder Enrich(Order order)
    {
        var subtotal = order.Units * order.UnitPrice;
        var taxable = Math.Max(0, subtotal - TaxFreeAllowance(order.Year));
        return new EnrichedOrder(
            order.Customer, order.Units, order.UnitPrice, order.Year,
            subtotal, taxable);
    }
}

public static class Reports
{
    public static decimal InvoiceTotal(Order order) => OrderEnricher.Enrich(order).Subtotal;

    public static decimal TaxDue(Order order) => OrderEnricher.Enrich(order).TaxableAmount * 0.2m;
}
```

Behavior is the same. The formulas now live in `Enrich`; a new derived value is one more
field there. If the enriched type should extend `Order` instead of repeating its fields, make
`Order` a non-sealed record and derive from it. The derived record takes the source in a copy
constructor (`EnrichedOrder(Order o, decimal subtotal, decimal taxable) : base(o)`), because a
`with` expression on an `Order` returns an `Order`, not an `EnrichedOrder`.

## C# notes
- This refactoring is idiomatic in JavaScript. In C# the transform is usually a function that
  returns a new enriched `record` (built with a constructor, or a copy constructor when it
  derives from the source record; `with` only fits when the enriched type is the same type),
  so the original is never mutated and no deep copy is needed.
- Records are shallow: if the source holds mutable collections or objects, copy them too.
- If the data does get mutated, or the derivations need the object's behavior, prefer
  Combine Functions into Class.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The transform leaves its input unchanged (the test from step 2).
