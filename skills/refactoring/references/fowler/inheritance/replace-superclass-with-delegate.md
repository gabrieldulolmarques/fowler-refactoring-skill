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
2. For each member of the superclass, add a forwarding member in the subclass that calls the same member on the field. Compile and test after each consistent group (a getter and its setter go together).
3. When every superclass member has a forwarder, remove the inheritance link (drop the `: Superclass` and the base constructor call). Compile and test.
4. Delete, one at a time, the forwarders for members that do not apply to the subclass, changing any caller the compiler reports. Compile and test after each.

With a very large superclass, such as a framework collection, forwarding every member is impractical. Forward the ones callers use, remove the link and let the compiler report the rest, as the example below does.
5. Check the model. The delegate is now a private component owned by one subclass instance. If instances should share the delegate, continue with Change Value to Reference ([change-value-to-reference.md](../organizing-data/change-value-to-reference.md)). Keep host-owned fields such as the id on the host.

## Example

Before: a listening history reuses `List<Play>` by inheritance, so callers can also insert, sort and clear it.

```csharp
using System.Collections.Generic;
using System.Linq;

public class Play
{
    public Play(string title, int seconds)
    {
        Title = title;
        Seconds = seconds;
    }

    public string Title { get; }
    public int Seconds { get; }
}

public class ListeningHistory : List<Play>
{
    public int TotalSeconds() => this.Sum(p => p.Seconds);
}

// caller
public class Caller
{
    public void Run()
    {
        var history = new ListeningHistory();
        history.Add(new Play("Blue Hour", 212));
        history.Clear(); // makes no sense for a history
    }
}
```

After step 1 and 2 (still inheriting, `new` hides the inherited members while both coexist):

```csharp
public class ListeningHistory : List<Play>
{
    private readonly List<Play> _plays = new();

    public new void Add(Play p) => _plays.Add(p);
    public new int Count => _plays.Count;
    public new IEnumerator<Play> GetEnumerator() => _plays.GetEnumerator();

    public int TotalSeconds() => _plays.Sum(p => p.Seconds);
}
```

`new` only hides members for callers that use the `ListeningHistory` type. A caller that reaches the object through `IEnumerable<Play>` (LINQ, or a `foreach` over an interface-typed variable) still hits the inherited, now empty, list until step 3, so check for such callers before relying on the tests after this stage.

After steps 3 and 4 (link removed; the compiler now rejects `Clear`):

```csharp
// fragment
using System.Collections;
using System.Collections.Generic;
using System.Linq;

public class ListeningHistory : IEnumerable<Play>
{
    private readonly List<Play> _plays = new();

    public void Add(Play p) => _plays.Add(p);
    public int Count => _plays.Count;
    public IEnumerator<Play> GetEnumerator() => _plays.GetEnumerator();
    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();

    public int TotalSeconds() => _plays.Sum(p => p.Seconds);
}
```

Behavior is the same for every remaining caller; only the members that did not apply are gone.

## Verification

- Compiles and the tests pass after every step; one commit per refactoring.
- No caller depended on a member that was dropped, or it was forwarded on purpose.
- Anything that treated the subclass as the superclass (casts, `is` checks, polymorphic parameters, collections of the base type) was found and changed.
