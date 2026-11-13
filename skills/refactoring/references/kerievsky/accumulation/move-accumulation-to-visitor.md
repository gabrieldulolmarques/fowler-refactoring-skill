# Move Accumulation to Visitor

Kerievsky (2004), ch. 10, p. 320. Pattern: Visitor. Direction: to, towards (Visitor); away (Iterator).

## When to use
Smells: Long Method, Switch Statements.

- A method gathers information from several classes that hold different data and expose different interfaces (heterogeneous classes), usually through type tests and casts.
- A Visitor does this through double dispatch: each class has an `Accept(visitor)` method that calls back the visitor's method for that class, passing itself. The visitor then reads what it needs without casts.
- Several different algorithms over the same structure can each be their own visitor, and a visitor can cross class hierarchies.
- The book's warning is that Visitor is rarely needed, and that when it is, the need is strong. Try simpler solutions first. If the classes can share a common interface (see [unify-interfaces.md](../utilities/unify-interfaces.md)), a Visitor is more than you need. Compare with [move-accumulation-to-collecting-parameter.md](move-accumulation-to-collecting-parameter.md) first.
- Liabilities: every new visitable class needs an `Accept` method and a visit method on every visitor, and visited classes may have to expose more of their data.

## Mechanics
The book gives three sets, depending on where the accumulation code lives. The accumulation method gathers data from the *accumulation sources* (the visited classes).

**External accumulation method** (the code lives in a class that is not one of the sources, the *host*)
1. If the host already has too many jobs, move the method into a new host first with Replace Function with Command ([replace-function-with-command.md](../../fowler/refactoring-apis/replace-function-with-command.md)).
2. Turn the local variables used across the accumulation logic into fields of the host. Compile and test.
3. For each source class, apply Extract Function ([extract-function.md](../../fowler/first-set/extract-function.md)) on its piece of the logic into a method taking that source as the argument, named `Accept`. Compile and test.
4. Extract the body of each `Accept` into a `VisitSourceName(source)` method.
5. Move each `Accept` method to its source class with Move Function ([move-function.md](../../fowler/moving-features/move-function.md)); it now takes the host as its argument. Compile and test.
6. Inline the `Accept` calls in the accumulation method ([inline-function.md](../../fowler/first-set/inline-function.md)). Compile and test.
7. Apply [../utilities/unify-interfaces.md](../utilities/unify-interfaces.md) on the sources' base class or interface so `Accept` can be called polymorphically.
8. Rewrite the accumulation method to call `Accept` on every source. Compile and test.
9. Extract an interface from the host declaring the visit methods (Extract Interface, 1st ed. only), and change every `Accept` to take that interface. Compile and test. The host is now a visitor.

**Internal accumulation method** (the method is implemented by the source classes themselves, in a hierarchy)
1. Create a new visitor class. Compile.
2. For each source class, add a `VisitSourceName(source)` method to the visitor, returning `void`. Compile.
3. In each source class, extract the body of the accumulation method into an `Accept` method with the same signature everywhere, so the accumulation methods become identical. Compile and test.
4. Pull the now identical accumulation method up to the base class ([pull-up-method.md](../../fowler/inheritance/pull-up-method.md)). Compile and test.
5. Add a visitor parameter to every `Accept` ([change-function-declaration.md](../../fowler/first-set/change-function-declaration.md)); the accumulation method passes a new visitor. Compile.
6. For each source, move the accumulation code from `Accept` into the matching visit method on the visitor, leaving `Accept` as `visitor.VisitX(this)`. Compile and test.

**Visitor replacement** (neither form exists yet, but a visitor would be better)
1. Create a concrete visitor class. If it is the second one, extract a superclass for it (Extract Superclass, [extract-superclass.md](../../fowler/inheritance/extract-superclass.md)) and use that type in the `Accept` signatures.
2. For each source class, add a visit method on the visitor and an `Accept` method on the source that calls it with `this`. This gives the skeleton.
3. Give the visitor a way to read its accumulated result, initially empty.
4. In the accumulation method, create the visitor, call `Accept` on every source and use the visitor's result instead of the old one. Tests now fail.
5. Fill in each visit method by moving the code from the accumulation method. Give visit methods access to what they need, move variables used by several visit methods into visitor fields, and pass inputs through the visitor's constructor. Compile and test that results match.
6. Remove the old code from the accumulation method. Compile and test.
7. What remains iterates over objects and passes the visitor. If some of them have no `Accept`, give them a do-nothing one so the loop needs no type check.
8. Extract that loop into a method that takes the visitor and move it where other clients can reach it. Compile and test.

## Example
Before: a summary builder walks export records of different kinds and tests the type of each, reading different data from each.

```csharp
using System.Collections.Generic;

public abstract class ExportRecord { }

public class SaleRecord : ExportRecord
{
    public int Quantity { get; }
    public decimal UnitPrice { get; }

    public SaleRecord(int quantity, decimal unitPrice)
    {
        Quantity = quantity;
        UnitPrice = unitPrice;
    }
}

public class RefundRecord : ExportRecord
{
    public decimal Amount { get; }

    public RefundRecord(decimal amount) => Amount = amount;
}

public class AdjustmentRecord : ExportRecord
{
    public decimal Percent { get; }

    public AdjustmentRecord(decimal percent) => Percent = percent;
}

public class SummaryBuilder
{
    public decimal Net(IEnumerable<ExportRecord> records)
    {
        decimal sales = 0m, refunds = 0m, percent = 0m;
        foreach (var record in records)
        {
            if (record is SaleRecord s) sales += s.Quantity * s.UnitPrice;
            else if (record is RefundRecord r) refunds += r.Amount;
            else if (record is AdjustmentRecord a) percent += a.Percent;
        }
        return sales * (1m - percent / 100m) - refunds;
    }
}
```

After (external accumulation method): the summary builder is the visitor; each record accepts it and calls back the method for its own type. Precondition: the collection holds no `null` elements; the old loop skipped them, while `record.Accept(this)` would throw.

```csharp
public interface IRecordVisitor
{
    void VisitSale(SaleRecord record);
    void VisitRefund(RefundRecord record);
    void VisitAdjustment(AdjustmentRecord record);
}

public abstract class ExportRecord
{
    public abstract void Accept(IRecordVisitor visitor);
}

public class SaleRecord : ExportRecord
{
    public int Quantity { get; }
    public decimal UnitPrice { get; }

    public SaleRecord(int quantity, decimal unitPrice)
    {
        Quantity = quantity;
        UnitPrice = unitPrice;
    }

    public override void Accept(IRecordVisitor visitor) => visitor.VisitSale(this);
}

public class RefundRecord : ExportRecord
{
    public decimal Amount { get; }

    public RefundRecord(decimal amount) => Amount = amount;

    public override void Accept(IRecordVisitor visitor) => visitor.VisitRefund(this);
}

public class AdjustmentRecord : ExportRecord
{
    public decimal Percent { get; }

    public AdjustmentRecord(decimal percent) => Percent = percent;

    public override void Accept(IRecordVisitor visitor) => visitor.VisitAdjustment(this);
}

public class SummaryBuilder : IRecordVisitor
{
    private decimal _sales, _refunds, _percent;

    public void VisitSale(SaleRecord record) => _sales += record.Quantity * record.UnitPrice;
    public void VisitRefund(RefundRecord record) => _refunds += record.Amount;
    public void VisitAdjustment(AdjustmentRecord record) => _percent += record.Percent;

    public decimal Net(IEnumerable<ExportRecord> records)
    {
        _sales = _refunds = _percent = 0m;
        foreach (var record in records)
            record.Accept(this);
        return _sales * (1m - _percent / 100m) - _refunds;
    }
}
```

## C# notes
- On C# 9 and later, a `switch` expression with type patterns often solves the same problem with much less code. Use a Visitor only when several algorithms need the same structure, or when the type set is open to extension by other assemblies.
- A generic `IRecordVisitor<TResult>` with return values avoids mutable fields, at the cost of a more elaborate interface.
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Results equal the old method for every kind of source, including a collection that mixes kinds, and a collection with an unknown or empty case.
- Adding a new source class fails to compile until each visitor handles it.
