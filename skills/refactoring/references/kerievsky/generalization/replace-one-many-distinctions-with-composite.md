# Replace One/Many Distinctions with Composite

Kerievsky (2004), ch. 8, p. 224. Pattern: Composite. Direction: to.

## When to use
Smells: Duplicated Code.

- A class has one method that processes a single object and a near-twin that processes a collection of them. The two repeat the same logic.
- Clients must pass different shapes of data depending on how many objects they have, so their code is not uniform.
- Results cannot be combined well: for example, "A and B" is easy with a list, but "(A and B) or C" needs several calls and a manual merge of the results.
- A composite lets one method handle one object, many objects, or a tree of them, so clients make a single call.
- Do not use it when only the duplication bothers you and uniform clients and richer combinations do not matter: extracting the shared code may be enough, and a Composite would be overkill. The composite may also need runtime checks on what gets added, since the type system alone may not stop invalid children.

## Mechanics
Call the method that takes one object the one-object method, and the one that takes a collection the many-object method.

1. Create a composite class whose constructor takes the collection and which exposes it through a getter. In the many-object method, create an instance of it and read the collection only through that getter. Compile and test.
2. Apply Extract Function ([extract-function.md](../../fowler/first-set/extract-function.md)) to the code in the many-object method that works on the collection, make the new method public, and move it to the composite with Move Function ([move-function.md](../../fowler/moving-features/move-function.md)). Compile and test.
3. The many-object method should now be almost the same as the one-object method, except that it builds the composite. Remove any other differences. Compile and test.
4. Reduce the many-object method to one line: a call to the one-object method with the composite as argument. For that, the composite must share a type with what the one-object method accepts: make it implement the same interface or base class (extract an interface if none exists; Extract Interface has no 2nd-edition counterpart, 1st ed. only). Compile and test.
5. Inline the many-object method with Inline Function ([inline-function.md](../../fowler/first-set/inline-function.md)). Compile and test.
6. Apply Encapsulate Collection ([encapsulate-collection.md](../../fowler/encapsulation/encapsulate-collection.md)) to the composite: clients now call `Add` instead of passing a collection to the constructor, and the getter returns a read-only view. Compile and test.

## Example
Before: a moderation checker has a one-rule method and a many-rule method that repeat the same work.

```csharp
using System.Collections.Generic;

public class ChatMessage
{
    public string Id { get; }
    public string Text { get; }
    public ChatMessage(string id, string text) { Id = id; Text = text; }
}

public class ModerationResult
{
    public bool Allowed { get; }
    public IReadOnlyList<string> Violations { get; }
    public ModerationResult(bool allowed, IReadOnlyList<string> violations)
    {
        Allowed = allowed;
        Violations = violations;
    }
}

public interface IModerationRule
{
    IReadOnlyList<string> Violations(ChatMessage message);
}

public class MaxLength : IModerationRule
{
    public IReadOnlyList<string> Violations(ChatMessage m) =>
        m.Text.Length <= 2000 ? new List<string>() : new List<string> { "message too long" };
}

public class NoLinks : IModerationRule
{
    public IReadOnlyList<string> Violations(ChatMessage m) =>
        m.Text.Contains("http") ? new List<string> { "contains a link" } : new List<string>();
}

public class ModerationChecker
{
    public ModerationResult Check(ChatMessage message, IModerationRule rule)
    {
        var violations = rule.Violations(message);
        return new ModerationResult(violations.Count == 0, violations);
    }

    public ModerationResult CheckAll(ChatMessage message, List<IModerationRule> rules)
    {
        var violations = new List<string>();
        foreach (var rule in rules)
            violations.AddRange(rule.Violations(message));
        return new ModerationResult(violations.Count == 0, violations);
    }
}
```

After: `AllOf` is a composite rule. `CheckAll` is gone and callers pass one rule, whether it is a single rule or a group.

```csharp
using System.Collections.Generic;

public class ChatMessage
{
    public string Id { get; }
    public string Text { get; }
    public ChatMessage(string id, string text) { Id = id; Text = text; }
}

public class ModerationResult
{
    public bool Allowed { get; }
    public IReadOnlyList<string> Violations { get; }
    public ModerationResult(bool allowed, IReadOnlyList<string> violations)
    {
        Allowed = allowed;
        Violations = violations;
    }
}

public interface IModerationRule
{
    IReadOnlyList<string> Violations(ChatMessage message);
}

public class MaxLength : IModerationRule
{
    public IReadOnlyList<string> Violations(ChatMessage m) =>
        m.Text.Length <= 2000 ? new List<string>() : new List<string> { "message too long" };
}

public class NoLinks : IModerationRule
{
    public IReadOnlyList<string> Violations(ChatMessage m) =>
        m.Text.Contains("http") ? new List<string> { "contains a link" } : new List<string>();
}

public class AllOf : IModerationRule
{
    private readonly List<IModerationRule> _rules = new();
    public IReadOnlyList<IModerationRule> Rules => _rules;
    public void Add(IModerationRule rule) => _rules.Add(rule);

    public IReadOnlyList<string> Violations(ChatMessage message)
    {
        var violations = new List<string>();
        foreach (var rule in _rules)
            violations.AddRange(rule.Violations(message));
        return violations;
    }
}

public class ModerationChecker
{
    public ModerationResult Check(ChatMessage message, IModerationRule rule)
    {
        var violations = rule.Violations(message);
        return new ModerationResult(violations.Count == 0, violations);
    }
}

// A client now builds a group and makes one call:
//   var rules = new AllOf(); rules.Add(new MaxLength()); rules.Add(new NoLinks());
//   var result = new ModerationChecker().Check(message, rules);
```

A sibling composite such as `AnyOf` (passes when at least one child passes) can now be added without touching `ModerationChecker`; this is the "(A and B) or C" case the list version could not express in one call.

## C# notes
- Where a method takes `IEnumerable<T>` only to loop, check whether a composite is worth it: if clients never need nesting or other combinators, a `params`/`IEnumerable` overload with shared code may be enough.
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The violations reported for a group are the same, in the same order, as `CheckAll` gave before, and `Check` with a single rule is unchanged.
