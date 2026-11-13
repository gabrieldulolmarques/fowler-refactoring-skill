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
Before: a finder over the tool-call log of an assistant, with one method per combination.

```csharp
using System.Collections.Generic;

public enum CallStatus { Ok, Failed, TimedOut }

public class ToolCall
{
    public string Id { get; }
    public string Tool { get; }
    public CallStatus Status { get; }
    public int DurationMs { get; }
    public ToolCall(string id, string tool, CallStatus status, int durationMs)
    {
        Id = id;
        Tool = tool;
        Status = status;
        DurationMs = durationMs;
    }
}

public class ToolCallFinder
{
    private readonly List<ToolCall> _calls;
    public ToolCallFinder(List<ToolCall> calls) => _calls = calls;

    public List<ToolCall> ByStatus(CallStatus status)
    {
        var found = new List<ToolCall>();
        foreach (var c in _calls)
            if (c.Status == status) found.Add(c);
        return found;
    }

    public List<ToolCall> ByMinDuration(int minMs)
    {
        var found = new List<ToolCall>();
        foreach (var c in _calls)
            if (c.DurationMs >= minMs) found.Add(c);
        return found;
    }

    public List<ToolCall> ByStatusAndMinDuration(CallStatus status, int minMs)
    {
        var found = new List<ToolCall>();
        foreach (var c in _calls)
            if (c.Status == status && c.DurationMs >= minMs) found.Add(c);
        return found;
    }

    public List<ToolCall> ByToolNotStatus(string tool, CallStatus status)
    {
        var found = new List<ToolCall>();
        foreach (var c in _calls)
            if (c.Tool == tool && c.Status != status) found.Add(c);
        return found;
    }
}
```

After: a small set of specification classes and one `SelectBy`. Any combination is built by the caller.

```csharp
using System.Collections.Generic;
using System.Linq;

public enum CallStatus { Ok, Failed, TimedOut }

public class ToolCall
{
    public string Id { get; }
    public string Tool { get; }
    public CallStatus Status { get; }
    public int DurationMs { get; }
    public ToolCall(string id, string tool, CallStatus status, int durationMs)
    {
        Id = id;
        Tool = tool;
        Status = status;
        DurationMs = durationMs;
    }
}

public abstract class ToolCallSpec
{
    public abstract bool IsSatisfiedBy(ToolCall call);
}

public class StatusSpec : ToolCallSpec
{
    private readonly CallStatus _status;
    public StatusSpec(CallStatus status) => _status = status;
    public override bool IsSatisfiedBy(ToolCall c) => c.Status == _status;
}

public class MinDurationSpec : ToolCallSpec
{
    private readonly int _minMs;
    public MinDurationSpec(int minMs) => _minMs = minMs;
    public override bool IsSatisfiedBy(ToolCall c) => c.DurationMs >= _minMs;
}

public class ToolSpec : ToolCallSpec
{
    private readonly string _tool;
    public ToolSpec(string tool) => _tool = tool;
    public override bool IsSatisfiedBy(ToolCall c) => c.Tool == _tool;
}

public class AndSpec : ToolCallSpec
{
    private readonly ToolCallSpec[] _specs;
    public AndSpec(params ToolCallSpec[] specs) => _specs = specs;
    public override bool IsSatisfiedBy(ToolCall c) => _specs.All(s => s.IsSatisfiedBy(c));
}

public class OrSpec : ToolCallSpec
{
    private readonly ToolCallSpec[] _specs;
    public OrSpec(params ToolCallSpec[] specs) => _specs = specs;
    public override bool IsSatisfiedBy(ToolCall c) => _specs.Any(s => s.IsSatisfiedBy(c));
}

public class NotSpec : ToolCallSpec
{
    private readonly ToolCallSpec _spec;
    public NotSpec(ToolCallSpec spec) => _spec = spec;
    public override bool IsSatisfiedBy(ToolCall c) => !_spec.IsSatisfiedBy(c);
}

public class ToolCallFinder
{
    private readonly List<ToolCall> _calls;
    public ToolCallFinder(List<ToolCall> calls) => _calls = calls;

    public List<ToolCall> SelectBy(ToolCallSpec spec) => _calls.Where(spec.IsSatisfiedBy).ToList();
}

// Old ByToolNotStatus(t, s) is now:
//   finder.SelectBy(new AndSpec(new ToolSpec(t), new NotSpec(new StatusSpec(s))));
```

## C# notes
- In C#, a `Func<ToolCall, bool>` (and combinators over it) or LINQ `Where` is often all you need for in-memory filtering. Classes earn their place when the criteria must be inspected, printed, serialized or translated (for instance to SQL).
- If the target is a database, `Expression<Func<T, bool>>` lets a provider translate the criteria; building your own specification classes would then duplicate what the provider already does.
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- For each old finder method, a test builds the equivalent specification and returns the same calls in the same order before the old method is inlined.
