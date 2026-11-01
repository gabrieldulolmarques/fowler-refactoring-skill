# Collapse Hierarchy

Fowler (2018), ch. 12, p. 380. Formerly / aka: —. Inverse: —.

## When to use
Smells: Lazy Element, Speculative Generality.

- After pulling members up and pushing them down, a class and its parent may end up so
  similar that the split carries no meaning. Merge them.
- A base class with a single subclass, where no second subclass is planned, is the usual case.
- Do not collapse when the two classes still model a real distinction, or when other
  subclasses depend on the intermediate level.

## Mechanics
1. Decide which class survives. Prefer the name that will make the most sense going forward;
   if both are equally good, pick either.
2. Move every member of the class being removed into the survivor, one at a time, using the
   pull up / push down refactorings as needed ([pull-up-method.md](pull-up-method.md),
   [pull-up-field.md](pull-up-field.md), [push-down-method.md](push-down-method.md), [push-down-field.md](push-down-field.md)). Compile and
   test after each move.
3. Update every reference to the class being removed (declarations, casts, `new` calls,
   generic arguments, type checks) so it points at the survivor. Compile and test.
4. Delete the now empty class.
5. Compile and run the tests.

## Example
Before: `RegularInvoice` adds nothing the base needs to keep separate, and is the only
subclass.

```csharp
public class Invoice
{
    protected decimal Subtotal;

    public Invoice(decimal subtotal) => Subtotal = subtotal;

    public virtual decimal Total() => Subtotal;
}

public class RegularInvoice : Invoice
{
    private readonly decimal _tax;

    public RegularInvoice(decimal subtotal, decimal tax) : base(subtotal) => _tax = tax;

    public override decimal Total() => Subtotal + _tax;
}

// caller
Invoice invoice = new RegularInvoice(100m, 18m);
```

After: `Invoice` survives and absorbs the field, constructor parameter and behavior.

```csharp
public class Invoice
{
    private readonly decimal _subtotal;
    private readonly decimal _tax;

    public Invoice(decimal subtotal, decimal tax)
    {
        _subtotal = subtotal;
        _tax = tax;
    }

    public decimal Total() => _subtotal + _tax;
}

// caller
Invoice invoice = new Invoice(100m, 18m);
```

Same behavior: `Total()` returns 118 for the same inputs.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
