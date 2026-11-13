# Move Accumulation to Visitor

Kerievsky (2004), ch. 10, p. 320. Direction: to, towards (Visitor); away (Iterator). Pattern: Visitor (GoF, p. 331).

## When to use
Smells: Long Method, Switch Statements.

- A method gathers information from several classes that hold different data and expose different interfaces (heterogeneous classes), usually through type tests and casts.
- A Visitor does this through double dispatch: each class has an `Accept(visitor)` method that calls back the visitor's method for that class, passing itself. The visitor then reads what it needs without casts.
- Several different algorithms over the same structure can each be their own visitor, and a visitor can cross class hierarchies.
- The book's warning: most of the time you do not need a Visitor, but when you do you really need it. Consider simpler solutions first. If the classes can share a common interface (see [unify-interfaces.md](../utilities/unify-interfaces.md)), a Visitor is more than you need. Compare with [move-accumulation-to-collecting-parameter.md](move-accumulation-to-collecting-parameter.md) first.
- Liabilities: every new visitable class needs an `Accept` method and a visit method on every visitor, and visited classes may have to expose more of their data.

## Mechanics
The book gives three sets, depending on where the accumulation code lives. The accumulation method gathers data from the *accumulation sources* (the visited classes).

**External accumulation method** (the code lives in a class that is not one of the sources, the *host*)
1. If the host already has too many jobs, move the method into a new host first with Replace Function with Command ([replace-function-with-command.md](../refactoring-apis/replace-function-with-command.md)).
2. Turn the local variables used across the accumulation logic into fields of the host. Compile and test.
3. For each source class, apply Extract Function ([extract-function.md](../first-set/extract-function.md)) on its piece of the logic into a method taking that source as the argument, named `Accept`. Compile and test.
4. Extract the body of each `Accept` into a `VisitSourceName(source)` method.
5. Move each `Accept` method to its source class with Move Function ([move-function.md](../moving-features/move-function.md)); it now takes the host as its argument. Compile and test.
6. Inline the `Accept` calls in the accumulation method ([inline-function.md](../first-set/inline-function.md)). Compile and test.
7. Apply [../utilities/unify-interfaces.md](../utilities/unify-interfaces.md) on the sources' base class or interface so `Accept` can be called polymorphically.
8. Rewrite the accumulation method to call `Accept` on every source. Compile and test.
9. Extract an interface from the host declaring the visit methods (Extract Interface, 1st ed. only), and change every `Accept` to take that interface. Compile and test. The host is now a visitor.

**Internal accumulation method** (the method is implemented by the source classes themselves, in a hierarchy)
1. Create a new visitor class. Compile.
2. For each source class, add a `VisitSourceName(source)` method to the visitor, returning `void`. Compile.
3. In each source class, extract the body of the accumulation method into an `Accept` method with the same signature everywhere, so the accumulation methods become identical. Compile and test.
4. Pull the now identical accumulation method up to the base class ([pull-up-method.md](../inheritance/pull-up-method.md)). Compile and test.
5. Add a visitor parameter to every `Accept` ([change-function-declaration.md](../first-set/change-function-declaration.md)); the accumulation method passes a new visitor. Compile.
6. For each source, move the accumulation code from `Accept` into the matching visit method on the visitor, leaving `Accept` as `visitor.VisitX(this)`. Compile and test.

**Visitor replacement** (neither form exists yet, but a visitor would be better)
1. Create a concrete visitor class. If it is the second one, extract a superclass or interface for it (Extract Superclass, [extract-superclass.md](../inheritance/extract-superclass.md)) and use that type in the `Accept` signatures.
2. For each source class, add a visit method on the visitor and an `Accept` method on the source that calls it with `this`. This gives the skeleton.
3. Give the visitor a way to read its accumulated result, initially empty.
4. In the accumulation method, create the visitor, call `Accept` on every source and use the visitor's result instead of the old one. Tests now fail.
5. Fill in each visit method by moving the code from the accumulation method. Give visit methods access to what they need, move variables used by several visit methods into visitor fields, and pass inputs through the visitor's constructor. Compile and test that results match.
6. Remove the old code from the accumulation method. Compile and test.
7. What remains iterates over objects and passes the visitor. If some of them have no `Accept`, give them a do-nothing one so the loop needs no type check.
8. Extract that loop into a method that takes the visitor and move it where other clients can reach it. Compile and test.

## Example
Before: a calculator walks charges of different kinds and tests the type of each, reading different data from each.

```csharp
public abstract class Charge { }

public class ProductCharge : Charge
{
    public int Qty { get; init; }
    public decimal UnitPrice { get; init; }
}

public class ShippingCharge : Charge
{
    public decimal Weight { get; init; }
    public decimal RatePerKg { get; init; }
}

public class DiscountCharge : Charge
{
    public decimal Percent { get; init; }
}

public class TotalCalculator
{
    public decimal Total(IEnumerable<Charge> charges)
    {
        decimal subtotal = 0m, shipping = 0m, percent = 0m;
        foreach (var charge in charges)
        {
            if (charge is ProductCharge p) subtotal += p.Qty * p.UnitPrice;
            else if (charge is ShippingCharge s) shipping += s.Weight * s.RatePerKg;
            else if (charge is DiscountCharge d) percent += d.Percent;
        }
        return subtotal * (1m - percent / 100m) + shipping;
    }
}
```

After (external accumulation method): the calculator is the visitor; each charge accepts it and calls back the method for its own type.

```csharp
public interface IChargeVisitor
{
    void VisitProduct(ProductCharge charge);
    void VisitShipping(ShippingCharge charge);
    void VisitDiscount(DiscountCharge charge);
}

public abstract class Charge
{
    public abstract void Accept(IChargeVisitor visitor);
}

public class ProductCharge : Charge
{
    public int Qty { get; init; }
    public decimal UnitPrice { get; init; }
    public override void Accept(IChargeVisitor visitor) => visitor.VisitProduct(this);
}

public class ShippingCharge : Charge
{
    public decimal Weight { get; init; }
    public decimal RatePerKg { get; init; }
    public override void Accept(IChargeVisitor visitor) => visitor.VisitShipping(this);
}

public class DiscountCharge : Charge
{
    public decimal Percent { get; init; }
    public override void Accept(IChargeVisitor visitor) => visitor.VisitDiscount(this);
}

public class TotalCalculator : IChargeVisitor
{
    private decimal _subtotal, _shipping, _percent;

    public void VisitProduct(ProductCharge charge) => _subtotal += charge.Qty * charge.UnitPrice;
    public void VisitShipping(ShippingCharge charge) => _shipping += charge.Weight * charge.RatePerKg;
    public void VisitDiscount(DiscountCharge charge) => _percent += charge.Percent;

    public decimal Total(IEnumerable<Charge> charges)
    {
        _subtotal = _shipping = _percent = 0m;
        foreach (var charge in charges)
            charge.Accept(this);
        return _subtotal * (1m - _percent / 100m) + _shipping;
    }
}
```

## C# notes
- On C# 9 and later, a `switch` expression with type patterns often solves the same problem with much less code. Use a Visitor only when several algorithms need the same structure, or when the type set is open to extension by other assemblies.
- The visitor holds state between visits, so a visitor instance is not thread-safe and should be created per use (the example resets its fields at the start of `Total`; creating a new calculator per call is safer).
- A generic `IChargeVisitor<TResult>` with return values avoids mutable fields, at the cost of a more elaborate interface.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Results equal the old method for every kind of source, including a collection that mixes kinds, and a collection with an unknown or empty case.
- Adding a new source class fails to compile until each visitor handles it.
