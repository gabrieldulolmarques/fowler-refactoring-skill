# Introduce Null Object

Kerievsky (2004), ch. 9, p. 301. Direction: to. Pattern: Null Object (not in GoF; the book credits Bobby Woolf).

## When to use
Smells: Conditional Complexity, Duplicated Code.

- The same null check on the same field appears in many places, each with the same fallback (do nothing, or return a default). New code that forgets the check can still fail with a null error.
- A Null Object is an instance of the same type that does nothing or returns harmless defaults, so callers can always call it. The field refers to it until a real object is assigned.
- It should shrink the code or keep it the same size. If the null object adds more lines than the checks it removes, do not use it.
- Liabilities: it complicates a design that has only one or two null checks; programmers who do not know about it may still write checks that never fire; and a subclass-based null object must override every public method added to its base later. Implementing an interface avoids that last risk.
- Relation to Fowler: [introduce-special-case.md](../conditional-logic/introduce-special-case.md) covers the general case. Kerievsky's mechanics target a narrower, common one: a class has null checks on a field only because the field is used before it is first assigned a real value.

## Mechanics
Follow [introduce-special-case.md](../conditional-logic/introduce-special-case.md) when the null logic exists for any other reason (for example, a lookup that finds nothing). For the early-use case, the source class is the one that must be protected from nulls:

1. Create the null object: make a new class implement the source class's interface, and if that interface does not exist yet, extract it first (Extract Interface, 1st ed. only). The alternative is to create an empty subclass of the source class (Extract Subclass, 1st ed. only). Compile.
2. For one null check, override the invoked method in the null object with the fallback behavior. Compile. Repeat for the other checks on the source class.
3. In a class that has null checks, initialize the field to a null object at the earliest moment, normally at construction. Leave the existing assignments of real objects as they are; the new assignment just comes first. Compile.
4. Remove every null check on that field in the class. Compile and test.
5. Repeat steps 3 and 4 for each class that has the check.

If many null objects get created, see whether [limit-instantiation-with-singleton.md](limit-instantiation-with-singleton.md) is worth it, after profiling.

## Example
Before: a notifier is attached once the customer's channel is known, so each use checks for null. See the Fowler file for the general form; here is the early-use case.

```csharp
public interface IShipmentNotifier
{
    void Dispatched(string orderId);
    void Delivered(string orderId);
}

public class Order
{
    private readonly string _id = "A-1";
    private IShipmentNotifier? _notifier;

    public void AttachNotifier(IShipmentNotifier notifier) => _notifier = notifier;

    public void Dispatch()
    {
        if (_notifier != null)
            _notifier.Dispatched(_id);
    }

    public void Deliver()
    {
        if (_notifier != null)
            _notifier.Delivered(_id);
    }
}
```

After: the field starts as a do-nothing notifier and the checks are gone.

```csharp
public sealed class NullShipmentNotifier : IShipmentNotifier
{
    public void Dispatched(string orderId) { }
    public void Delivered(string orderId) { }
}

public class Order
{
    private readonly string _id = "A-1";
    private IShipmentNotifier _notifier = new NullShipmentNotifier();

    public void AttachNotifier(IShipmentNotifier notifier) => _notifier = notifier;

    public void Dispatch() => _notifier.Dispatched(_id);

    public void Deliver() => _notifier.Delivered(_id);
}
```

## C# notes
- With nullable reference types on, the field changes from `IShipmentNotifier?` to `IShipmentNotifier`, and the compiler then stops warning about it.
- Prefer an interface plus a `sealed` null class over subclassing, so a new interface method cannot be forgotten by inheritance.
- A stateless null object can be a shared static instance (`NullShipmentNotifier.Instance`).

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- No null check on the field remains, and a test that calls the methods before any real object is attached passes without an exception.
- Nobody relied on a returned null to mean "absent"; search for callers that test for it.
