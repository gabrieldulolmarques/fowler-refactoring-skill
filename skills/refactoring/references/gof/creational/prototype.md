# Prototype

Gamma et al. (1995), ch. 3, p. 117. Category: object creational.

## Intent
Create new objects by copying a configured instance (the prototype), so a client can produce objects without knowing their classes or how they are set up.

## When it pays off
- The classes to create are chosen at runtime, or you want to avoid a hierarchy of factories that mirrors the hierarchy of products.
- Instances of a class differ only in a few combinations of state, so it is easier to keep a few ready-made instances and clone them than to build each from scratch.
- New kinds of object can be defined by registering a configured instance, adding and removing them at runtime, with no new class.
- It reduces subclassing, and users can define "new kinds" by varying values or structure.
- Liability: every prototype class must implement a correct clone, which can be hard when the object holds shared resources or circular references.
- Not worth it when constructing the object is cheap and obvious, or when objects are immutable (share the same instance instead).

## Participants in C#
- **Prototype** (`IPrototype<T>`): interface declaring `Clone()`. `ICloneable` exists but returns `object`, so a typed interface is better.
- **ConcretePrototype** (`BillingPlan`): implements `Clone()`.
- **Client** (`PlanCatalog`): stores prototypes under keys and creates new objects by cloning them.

## Example (C#)
A SaaS billing system offers a few base plans. Sales creates customer-specific plans as copies of a base plan with a changed price, and the catalog never needs to know more than the plan type.

```csharp
using System;
using System.Collections.Generic;

public interface IPrototype<T>
{
    T Clone();
}

public class BillingPlan : IPrototype<BillingPlan>
{
    public string Name { get; set; }
    public decimal MonthlyPrice { get; set; }
    public List<string> Features { get; }

    public BillingPlan(string name, decimal monthlyPrice, IEnumerable<string> features)
    {
        Name = name;
        MonthlyPrice = monthlyPrice;
        Features = new List<string>(features);
    }

    // deep copy: the clone owns its own feature list
    public BillingPlan Clone() => new BillingPlan(Name, MonthlyPrice, Features);
}

public class PlanCatalog
{
    private readonly Dictionary<string, BillingPlan> _prototypes = new();

    public void Register(string key, BillingPlan prototype) => _prototypes[key] = prototype;

    public bool Unregister(string key) => _prototypes.Remove(key);

    public BillingPlan Create(string key)
    {
        if (!_prototypes.TryGetValue(key, out var prototype))
            throw new KeyNotFoundException("No plan registered as " + key);
        return prototype.Clone();
    }
}

public static class Program
{
    public static void Main()
    {
        var catalog = new PlanCatalog();
        catalog.Register("starter", new BillingPlan("Starter", 9m, new[] { "1 project" }));
        catalog.Register("team", new BillingPlan("Team", 49m, new[] { "10 projects", "SSO" }));

        BillingPlan custom = catalog.Create("team");
        custom.Name = "Team (Acme)";
        custom.MonthlyPrice = 39m;
        custom.Features.Add("Priority support");

        Console.WriteLine(catalog.Create("team").Features.Count); // 2: the prototype is untouched
    }
}
```

## Variations
- **Prototype manager.** When prototypes come and go at runtime, keep a registry (`PlanCatalog`) that registers, removes and looks them up by key, so clients do not manage prototypes themselves.
- **Shallow versus deep copy.** Decide what is shared and what is copied. `MemberwiseClone()` is a shallow copy: reference fields (like `Features`) would be shared. Copy every mutable reference the clone must own.
- **Initializing the clone.** The clone often needs values (a customer name, an id). Parameters on `Clone()` break the uniform interface, so set properties after cloning, or add an `Initialize(...)` method on the concrete class.
- **Serialization copy.** If the object can already be serialized and deserialized, a round trip produces a deep copy for free, at a performance cost.
- **Prototype-based factory.** A factory that holds one prototype per product and clones it (see [abstract-factory.md](abstract-factory.md)).

## Risks and C# alternatives
- Forgetting to deep-copy a mutable field gives two objects that silently change each other. Test that mutating the clone leaves the prototype intact (see Verification).
- A copy constructor (`new BillingPlan(other)`) is a common and explicit alternative to a `Clone()` method, and needs no cloning interface.
- For immutable objects there is nothing to protect: share one instance and create variations with a method that returns a new object (`plan.WithPrice(39m)`).
- Avoid `ICloneable`: its contract does not say shallow or deep, and it returns `object`.
- Value types (`struct`) are copied on assignment already; a prototype is only needed for reference types.

## Related patterns
- [Abstract Factory](abstract-factory.md): a competitor and a partner; a factory can store prototypes and return clones.
- [Factory Method](factory-method.md): a different way to vary created classes, through subclassing of the creator.
- [Composite](../structural/composite.md) and [Decorator](../structural/decorator.md): designs heavy in these often benefit from Prototype, since copying a whole structure is handy.

## Verification
- Cloning returns an independent object: changing the clone does not change the prototype, including nested collections.
- Adding a new variant of the product needs a registration, not a new class or factory.
- Every concrete prototype overrides `Clone()` so that the clone has the same runtime type.
- If the clones are never customized and the objects never change, check that sharing one immutable instance would not be enough.
