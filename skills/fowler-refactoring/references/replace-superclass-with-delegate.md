# Replace Superclass with Delegate

Fowler (2018), ch. 12, p. 399. Formerly / aka: Replace Inheritance with Delegation. Inverse: —.

## When to use

Smells: Refused Bequest, Insider Trading, Middle Man.

- Inheritance was used only to reuse code, and the subclass exposes superclass members that do not apply to it (a stack that is a list and so allows inserting in the middle).
- "Every instance of the subclass is a valid superclass instance" is false. A typical case is a type and its instance mixed up: a product description class reused as the base of a physical item that has a serial number.
- The subclass breaks whenever the superclass changes, because the coupling is tight.

When not to use it: if every superclass member applies to the subclass and every subclass instance is a legitimate superclass instance, inheritance is simple and effective. Inheritance is a fine default; switch when it starts to hurt. The cost is a forwarding method for each member you keep.

## Mechanics

1. In the subclass, add a field of the superclass type and initialize it with a new instance (usually built with the same constructor arguments).
2. For each superclass member the callers use, add a forwarding method in the subclass that calls the same member on the field. Compile and test after each consistent group (a getter and its setter go together).
3. When every member that is still needed has a forwarder, remove the inheritance link (drop the `: Superclass` and the base constructor call).
4. Fix what the compiler reports: members that were used through inheritance and were not forwarded. Forward them if they make sense, or change the caller.
5. Check the model. The delegate is now a private component owned by one subclass instance. If instances should share the delegate, continue with Change Value to Reference ([change-value-to-reference.md](change-value-to-reference.md)). Keep host-owned fields such as the id on the host.

## Example

Before: a statement reuses `List<Transaction>` by inheritance, so callers can also insert, sort and clear it.

```csharp
public record Transaction(DateOnly Date, decimal Amount);

public class Statement : List<Transaction>
{
    public decimal Balance() => this.Sum(t => t.Amount);
}

// caller
var statement = new Statement();
statement.Add(new Transaction(new DateOnly(2026, 1, 5), 120m));
statement.Clear(); // makes no sense for a statement
```

After step 1 and 2 (still inheriting, `new` hides the inherited members while both coexist):

```csharp
public class Statement : List<Transaction>
{
    private readonly List<Transaction> _transactions = new();

    public new void Add(Transaction t) => _transactions.Add(t);
    public new int Count => _transactions.Count;
    public new IEnumerator<Transaction> GetEnumerator() => _transactions.GetEnumerator();

    public decimal Balance() => _transactions.Sum(t => t.Amount);
}
```

`new` only hides members for callers that use the `Statement` type. A caller that reaches the object through `IEnumerable<Transaction>` (LINQ, or a `foreach` over an interface-typed variable) still hits the inherited, now empty, list until step 3, so check for such callers before relying on the tests after this stage.

After step 3 (link removed; the compiler now rejects `Clear`):

```csharp
using System.Collections;

public class Statement : IEnumerable<Transaction>
{
    private readonly List<Transaction> _transactions = new();

    public void Add(Transaction t) => _transactions.Add(t);
    public int Count => _transactions.Count;
    public IEnumerator<Transaction> GetEnumerator() => _transactions.GetEnumerator();
    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();

    public decimal Balance() => _transactions.Sum(t => t.Amount);
}
```

Behavior is the same for every remaining caller; only the members that did not apply are gone.

## Verification

- Compiles and the tests pass after every step; one commit per refactoring.
- No caller depended on a member that was dropped, or it was forwarded on purpose.
- Anything that treated the subclass as the superclass (casts, `is` checks, polymorphic parameters, collections of the base type) was found and changed.
