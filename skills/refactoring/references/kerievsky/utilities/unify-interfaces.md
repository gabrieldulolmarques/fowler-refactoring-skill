# Unify Interfaces

Kerievsky (2004), ch. 11, p. 343. Pattern: —. Direction: —.

## When to use
Smells: Duplicated Code (the book's inside back cover lists Unify Interfaces with Adapter there; this utility is the low-level step it builds on).

- A superclass or interface lacks public methods that a subclass has, so code cannot treat them all the same way and falls back on type checks or casts.
- Add the missing methods to the base type, with do-nothing (null) behavior in a class, so the subclass can override them and callers can use the base type everywhere.
- The book needed it twice: when a Decorator needed the same interface as the class it embellishes ([move-embellishment-to-decorator.md](../simplification/move-embellishment-to-decorator.md)), and when a Visitor needed its sources to accept it polymorphically ([move-accumulation-to-visitor.md](../accumulation/move-accumulation-to-visitor.md)).
- It is often a temporary step. Later refactorings may let you remove the added methods again, or you may extract a stand-alone interface so that implementors do not inherit the base class's fields.

## Mechanics
For each *missing method*, a public method on the subclass that the superclass or interface does not declare:
1. Add a copy of the method to the superclass or interface. In a superclass, give it a body that does nothing, or returns a harmless default. Compile.
2. Repeat until the two share the same public interface.
3. Test everything that uses the superclass.

## Example
Before: only the express subclass can notify the customer, so a loop over shipments has to check the type.

```csharp
public interface ICustomerNotifier { void Send(string message); }

public class Shipment
{
    public string Id { get; init; } = "";
    public virtual decimal Cost() => 5m;
}

public class ExpressShipment : Shipment
{
    public override decimal Cost() => 15m;
    public void Notify(ICustomerNotifier notifier) => notifier.Send($"Shipment {Id} is on its way");
}
```

After: `Notify` is declared on the base class with null behavior and overridden in the subclass, so callers use `Shipment` alone.

```csharp
public class Shipment
{
    public string Id { get; init; } = "";
    public virtual decimal Cost() => 5m;
    public virtual void Notify(ICustomerNotifier notifier) { }
}

public class ExpressShipment : Shipment
{
    public override decimal Cost() => 15m;
    public override void Notify(ICustomerNotifier notifier) => notifier.Send($"Shipment {Id} is on its way");
}

public static class Demo
{
    public static void NotifyAll(IEnumerable<Shipment> shipments, ICustomerNotifier notifier)
    {
        foreach (var s in shipments) s.Notify(notifier);
    }
}
```

## C# notes
- The base method must be `virtual` (or `abstract`) and the subclass method `override`. A subclass method of the same name without `override` hides the base one and `Notify` through a `Shipment` reference would do nothing.
- For an interface, adding a member breaks every existing implementor. Default interface methods (C# 8) let you add it with a body, but they are only reachable through the interface type, not the class.
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The type checks or casts the unification was meant to remove can now be deleted, and tests that use only the base type still pass for each subclass.
