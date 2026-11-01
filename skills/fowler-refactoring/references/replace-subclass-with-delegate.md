# Replace Subclass with Delegate

Fowler (2018), ch. 12, p. 381. Formerly / aka: none. Inverse: none listed in the catalog
(Remove Subclass and Collapse Hierarchy go the other way for simple cases).

## When to use
Smells: Insider Trading, Refused Bequest, Middle Man.

- Inheritance gives one axis of variation only. If the same class must also vary by a second
  criterion, one of the two must become a delegate.
- The variant must change during the object's life (a regular order becomes a priority order),
  and replacing the object is not practical because many places hold a reference to it.
- The subclass and superclass are so entangled that changing the parent keeps breaking the
  child, especially across modules or teams.

When not to use: if inheritance fits well and none of the above applies, keep it. The result
has dispatch logic and a two-way reference, so the refactoring alone rarely makes the code
simpler; the payoff is the freedom it buys. Prefer inheritance first and move to a delegate
when it starts to hurt.

## Mechanics
1. If many callers construct the subclass, wrap construction first with Replace Constructor
   with Factory Function ([replace-constructor-with-factory-function.md](replace-constructor-with-factory-function.md)).
2. Create an empty delegate class. Its constructor takes the data only the subclass uses and,
   usually, a back-reference to the host (the superclass instance).
3. Add a field to the superclass that holds the delegate (null when there is none).
4. Make the creation code (factory or constructor) build the delegate and store it in that
   field.
5. Pick one method of the subclass and move it to the delegate with Move Function
   ([move-function.md](move-function.md)). Reach host data through the back-reference; move data that only
   the subclass uses into the delegate. Leave a forwarding method in the subclass for now.
   Test.
6. If the superclass method has callers outside the hierarchy, give the superclass method
   dispatch logic: use the delegate when present, otherwise the original behavior. If the
   subclass method called the base implementation, either extract the base calculation into
   its own method that the delegate can call, or turn the delegate method into an extension of
   the base result (the host passes its result in). Do not call the host's own virtual
   method from the delegate: that recurses forever. If the method exists only in the subclass,
   dispatch with a sensible default for the no-delegate case. Test.
7. If the method has no outside callers, just remove the subclass method (Remove Dead Code,
   [remove-dead-code.md](remove-dead-code.md)). Test.
8. Repeat steps 5 to 7 for every member of the subclass.
9. When several subclasses become delegates and defaults get duplicated, apply Extract
   Superclass ([extract-superclass.md](extract-superclass.md)) on the delegates and always create some delegate,
   so the host's dispatch needs no null check and delegates keep the default behavior.
   Never branch on the delegate's concrete type.
10. Change every construction of the subclass to build the superclass. Test.
11. Delete the now empty subclass.

## Example
Before: wholesale invoices are a subclass.

```csharp
public class Invoice
{
    protected readonly decimal Subtotal;

    public Invoice(decimal subtotal) => Subtotal = subtotal;

    public virtual decimal Total => Subtotal;
    public virtual bool AllowsInstallments => Subtotal > 1000m;
}

public class WholesaleInvoice : Invoice
{
    private readonly decimal _discountRate;

    public WholesaleInvoice(decimal subtotal, decimal discountRate) : base(subtotal)
        => _discountRate = discountRate;

    public override decimal Total => decimal.Round(base.Total * (1 - _discountRate), 2);
    public override bool AllowsInstallments => true;
    public decimal SavedAmount => Subtotal - Total;
}
```

After: the wholesale behavior lives in a delegate, so an invoice can become wholesale at
runtime and the base class stays free for another use of inheritance.

```csharp
public class Invoice
{
    private WholesaleDelegate? _wholesale;

    internal decimal Subtotal { get; }

    private Invoice(decimal subtotal) => Subtotal = subtotal;

    public static Invoice Create(decimal subtotal) => new Invoice(subtotal);

    public static Invoice CreateWholesale(decimal subtotal, decimal discountRate)
    {
        var invoice = new Invoice(subtotal);
        invoice.BecomeWholesale(discountRate);
        return invoice;
    }

    public void BecomeWholesale(decimal discountRate)
        => _wholesale = new WholesaleDelegate(this, discountRate);

    public decimal Total
    {
        get
        {
            var result = Subtotal;
            return _wholesale is null ? result : _wholesale.ExtendTotal(result);
        }
    }

    public bool AllowsInstallments
        => _wholesale is null ? Subtotal > 1000m : _wholesale.AllowsInstallments;

    public decimal? SavedAmount => _wholesale?.SavedAmount;
}

internal class WholesaleDelegate
{
    private readonly Invoice _host;
    private readonly decimal _discountRate;

    public WholesaleDelegate(Invoice host, decimal discountRate)
    {
        _host = host;
        _discountRate = discountRate;
    }

    public decimal ExtendTotal(decimal baseTotal) => decimal.Round(baseTotal * (1 - _discountRate), 2);
    public bool AllowsInstallments => true;
    public decimal SavedAmount => _host.Subtotal - _host.Total;
}
```

Behavior is unchanged for callers that go through `Invoice.Create` and
`Invoice.CreateWholesale`; the `WholesaleInvoice` class is gone.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Tests cover both variants of every moved method, including the base-call case and a switch
  of variant at runtime if the delegate is meant to be replaceable.
- No caller still constructs the removed subclass or checks the delegate's concrete type.
