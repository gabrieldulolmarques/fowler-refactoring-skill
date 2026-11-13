# Interpreter

Gamma et al. (1995), ch. 5, p. 243. Category: class behavioral.

## Intent
For a small language, represent its grammar as a set of classes and write an interpreter that evaluates sentences of the language, held as trees of those classes.

## When it pays off
- A problem recurs often enough that expressing instances as sentences of a small language is worth it (matching rules, filters, pricing rules, feature-flag targeting).
- The grammar is simple and performance is not critical. Each grammar rule becomes a class, so the pattern scales badly to large grammars.
- Benefits: the grammar is easy to change and extend by adding or editing classes, and each node class is short and similar to the others.
- Liabilities: many rules mean many classes that are hard to maintain, and walking a tree is not the fastest way to evaluate. For large or hot languages, use a parser generator or compile the tree to another form.
- Not worth it when a few `if` statements or a lookup table covers the cases, or when a real expression library already exists.

## Participants in C#
- **AbstractExpression** (`IFlagRule`): interface with the `Evaluate` operation shared by every node.
- **TerminalExpression** (`AttributeEquals`): a leaf. Implements the base case of the recursion.
- **NonterminalExpression** (`AndRule`, `OrRule`, `NotRule`): one class per composite grammar rule. Holds sub-expressions and evaluates them recursively.
- **Context** (`UserContext`): global information the evaluation reads (here, user attributes).
- **Client** (`Program`): builds the tree, or receives it from a parser, then calls `Evaluate`.

## Example (C#)
A feature flag is enabled for users matching a targeting rule. The mini grammar is `rule := attribute = value | rule AND rule | rule OR rule | NOT rule`. The client assembles the tree by hand; a parser would produce the same tree from text.

```csharp
using System;
using System.Collections.Generic;

public class UserContext
{
    private readonly Dictionary<string, string> _attributes;

    public UserContext(Dictionary<string, string> attributes) => _attributes = attributes;

    public string? Get(string name) => _attributes.TryGetValue(name, out var v) ? v : null;
}

public interface IFlagRule
{
    bool Evaluate(UserContext context);
}

public class AttributeEquals : IFlagRule
{
    private readonly string _name;
    private readonly string _value;

    public AttributeEquals(string name, string value)
    {
        _name = name;
        _value = value;
    }

    public bool Evaluate(UserContext context) => context.Get(_name) == _value;
}

public class AndRule : IFlagRule
{
    private readonly IFlagRule _left;
    private readonly IFlagRule _right;

    public AndRule(IFlagRule left, IFlagRule right)
    {
        _left = left;
        _right = right;
    }

    public bool Evaluate(UserContext context) => _left.Evaluate(context) && _right.Evaluate(context);
}

public class OrRule : IFlagRule
{
    private readonly IFlagRule _left;
    private readonly IFlagRule _right;

    public OrRule(IFlagRule left, IFlagRule right)
    {
        _left = left;
        _right = right;
    }

    public bool Evaluate(UserContext context) => _left.Evaluate(context) || _right.Evaluate(context);
}

public class NotRule : IFlagRule
{
    private readonly IFlagRule _inner;

    public NotRule(IFlagRule inner) => _inner = inner;

    public bool Evaluate(UserContext context) => !_inner.Evaluate(context);
}

public static class Program
{
    public static void Main()
    {
        // country = BR AND (plan = pro OR beta = true) AND NOT role = staff
        IFlagRule rule = new AndRule(
            new AndRule(
                new AttributeEquals("country", "BR"),
                new OrRule(new AttributeEquals("plan", "pro"), new AttributeEquals("beta", "true"))),
            new NotRule(new AttributeEquals("role", "staff")));

        var user = new UserContext(new Dictionary<string, string>
        {
            ["country"] = "BR",
            ["plan"] = "free",
            ["beta"] = "true",
        });

        Console.WriteLine(rule.Evaluate(user)); // True
    }
}
```

## Variations
- **Building the tree.** The pattern does not say how the tree is created. Use a hand-written recursive-descent parser, a table-driven one, or build the tree in code as above.
- **Where `Evaluate` lives.** If the language will get many operations (evaluate, print, validate, optimize), put them in a visitor ([visitor.md](visitor.md)) so the node classes stay unchanged. If there is a single operation, keep it in the nodes.
- **Sharing terminals.** If the same terminal appears many times, a single instance can be shared, as long as position-specific data is passed in through the context and not stored in the node. See [Flyweight](../structural/flyweight.md).
- **Mutable context.** The context can also carry results or state that nodes update, for example variable bindings, when evaluation has side effects.

## Risks and C# alternatives
- Do not grow the grammar by habit. Past a handful of rules, a parser library or generator is a better fit than one class per rule.
- In C#, a lambda tree can replace the class hierarchy. `Func<UserContext, bool>` combinators (`And(a, b)` returning a new lambda) express the same rules with less ceremony when you do not need to inspect or print the tree.
- `System.Linq.Expressions` already offers an expression tree that can be compiled to a delegate, which is the compile-to-another-form route for hot paths.
- Pattern matching and `switch` expressions over a closed set of node types are an alternative to virtual `Evaluate`, and they keep the operation outside the nodes.
- Rules that come from users are untrusted input. Validate the sentence and bound recursion depth and cost.

## Related patterns
- [Composite](../structural/composite.md): the syntax tree is a composite.
- [Flyweight](../structural/flyweight.md): shares terminal symbols in the tree.
- [Iterator](iterator.md): can traverse the structure.
- [Visitor](visitor.md): keeps each operation on the nodes in one class instead of spread across node classes.

## Verification
- Each node class has a test, and a few whole sentences are tested end to end, including negation and nesting.
- The evaluation reads only the context and the tree, with no hidden global state.
- Adding a new rule type means adding one class, not editing the others.
- The number of node classes is still small. If it keeps growing, reconsider a parser generator.
