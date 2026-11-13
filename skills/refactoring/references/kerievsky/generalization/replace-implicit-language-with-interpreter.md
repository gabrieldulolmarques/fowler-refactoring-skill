# Replace Implicit Language with Interpreter

Kerievsky (2004), ch. 8, p. 269. Pattern: Interpreter. Direction: to.

## When to use
Smells: Combinatorial Explosion, Large Class, Primitive Obsession, Duplicated Code.

- A class has many methods that are really combinations of a few ideas: `ByStatus`, `ByMinTotal`, `ByStatusAndMinTotal`, `ByCustomerAndStatus`... The language of "find orders that are X and Y, but not Z" is there, but never written down as such. Each new combination means a new method, and the methods repeat the same filtering code.
- Modeling the language with a few small classes (the criteria, plus and/or/not) lets callers build any combination at run time with no new code, and lets behavior be configured dynamically, for example from a search form.
- This is the Specification pattern and the Query Object pattern, which are interpreters for object selection.
- It fits small grammars (fewer than about a dozen classes). For a large language, a parser generator is better. For a tiny uniform one, plain code may be enough.
- There is a start-up cost: defining the classes and changing callers to compose them. It pays off when the alternative is a growing list of near-duplicate methods.

## Mechanics
These steps assume object selection: several methods each loop over a collection and pick the objects that match.

1. Find a selection method that uses one criterion argument (for example a minimum total). Create a concrete specification class for that criterion: its constructor takes the value and it exposes a getter. In the selection method, create an instance and read the criterion through the getter. Name the class for what it does (`MinTotalSpec`). If a method uses several criteria, do steps 1 and 2 for each one. Compile and test that selection still works.
2. Apply Extract Function ([extract-function.md](../../fowler/first-set/extract-function.md)) to the condition inside the loop, giving a boolean method `IsSatisfiedBy`, and move it to the concrete specification with Move Function ([move-function.md](../../fowler/moving-features/move-function.md)). If no specification superclass exists yet, create one with Extract Superclass ([extract-superclass.md](../../fowler/inheritance/extract-superclass.md)), abstract, declaring only `IsSatisfiedBy`. Compile and test.
3. Repeat steps 1 and 2 for the other selection methods.
4. For a selection method that now builds several concrete specifications, create a composite specification that holds them (via constructor or an `Add` method), move the combined condition into its `IsSatisfiedBy`, and make it extend the specification superclass (see [replace-one-many-distinctions-with-composite.md](replace-one-many-distinctions-with-composite.md) and [extract-composite.md](extract-composite.md)). Add `Or` and `Not` specifications when callers need them.
5. Every selection method now takes one specification and the methods are identical except for how the specification is built. Extract the shared loop into `SelectBy(spec)` and make each selection method call it. Compile and test after each.
6. Inline the old selection methods with Inline Function ([inline-function.md](../../fowler/first-set/inline-function.md)) so callers build the specification and call `SelectBy`. Compile and test.

## Example
Before: an order finder with one method per combination.

```csharp
using System.Collections.Generic;

public enum Status { Open, Paid, Shipped }
public record Order(string Id, string Customer, Status Status, decimal Total);

public class OrderFinder
{
    private readonly List<Order> _orders;
    public OrderFinder(List<Order> orders) => _orders = orders;

    public List<Order> ByStatus(Status status)
    {
        var found = new List<Order>();
        foreach (var o in _orders)
            if (o.Status == status) found.Add(o);
        return found;
    }

    public List<Order> ByMinTotal(decimal min)
    {
        var found = new List<Order>();
        foreach (var o in _orders)
            if (o.Total >= min) found.Add(o);
        return found;
    }

    public List<Order> ByStatusAndMinTotal(Status status, decimal min)
    {
        var found = new List<Order>();
        foreach (var o in _orders)
            if (o.Status == status && o.Total >= min) found.Add(o);
        return found;
    }

    public List<Order> ByCustomerNotStatus(string customer, Status status)
    {
        var found = new List<Order>();
        foreach (var o in _orders)
            if (o.Customer == customer && o.Status != status) found.Add(o);
        return found;
    }
}
```

After: a small set of specification classes and one `SelectBy`. Any combination is built by the caller.

```csharp
using System.Collections.Generic;
using System.Linq;

public enum Status { Open, Paid, Shipped }
public record Order(string Id, string Customer, Status Status, decimal Total);

public abstract class OrderSpec
{
    public abstract bool IsSatisfiedBy(Order order);
}

public class StatusSpec : OrderSpec
{
    private readonly Status _status;
    public StatusSpec(Status status) => _status = status;
    public override bool IsSatisfiedBy(Order o) => o.Status == _status;
}

public class MinTotalSpec : OrderSpec
{
    private readonly decimal _min;
    public MinTotalSpec(decimal min) => _min = min;
    public override bool IsSatisfiedBy(Order o) => o.Total >= _min;
}

public class CustomerSpec : OrderSpec
{
    private readonly string _customer;
    public CustomerSpec(string customer) => _customer = customer;
    public override bool IsSatisfiedBy(Order o) => o.Customer == _customer;
}

public class AndSpec : OrderSpec
{
    private readonly OrderSpec[] _specs;
    public AndSpec(params OrderSpec[] specs) => _specs = specs;
    public override bool IsSatisfiedBy(Order o) => _specs.All(s => s.IsSatisfiedBy(o));
}

public class OrSpec : OrderSpec
{
    private readonly OrderSpec[] _specs;
    public OrSpec(params OrderSpec[] specs) => _specs = specs;
    public override bool IsSatisfiedBy(Order o) => _specs.Any(s => s.IsSatisfiedBy(o));
}

public class NotSpec : OrderSpec
{
    private readonly OrderSpec _spec;
    public NotSpec(OrderSpec spec) => _spec = spec;
    public override bool IsSatisfiedBy(Order o) => !_spec.IsSatisfiedBy(o);
}

public class OrderFinder
{
    private readonly List<Order> _orders;
    public OrderFinder(List<Order> orders) => _orders = orders;

    public List<Order> SelectBy(OrderSpec spec) => _orders.Where(spec.IsSatisfiedBy).ToList();
}

// Old ByCustomerNotStatus(c, s) is now:
//   finder.SelectBy(new AndSpec(new CustomerSpec(c), new NotSpec(new StatusSpec(s))));
```

## C# notes
- In C#, a `Func<Order, bool>` (and combinators over it) or LINQ `Where` is often all you need for in-memory filtering. Classes earn their place when the criteria must be inspected, printed, serialized or translated (for instance to SQL).
- If the target is a database, `Expression<Func<T, bool>>` lets a provider translate the criteria; building your own specification classes would then duplicate what the provider already does.
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- For each old finder method, a test builds the equivalent specification and returns the same orders in the same order before the old method is inlined.
