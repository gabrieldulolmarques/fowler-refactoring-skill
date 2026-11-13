# Replace Implicit Tree with Composite

Kerievsky (2004), ch. 7, p. 178. Direction: to. Pattern: Composite (GoF, p. 163).

## When to use
Smells: Primitive Obsession.

- Data or logic forms a tree without being modeled as one: nested loops that print or total a hierarchy, strings assembled with hand-written indentation and closing markers, tuples and dictionaries standing in for nodes. Every change to the shape (a new level, a different format) means editing the construction code.
- A Composite gives each part a class and lets parents treat all children through one interface, so formatting, totaling and closing are done once, by the nodes.
- For conditional logic (a tree of `&&` / `||` tests) the refactoring only pays off when many similar conditions are piling up; that case is [replace-implicit-language-with-interpreter.md](../generalization/replace-implicit-language-with-interpreter.md).
- If the client must build the same tree in several output forms, add a Builder on top afterwards ([encapsulate-composite-with-builder.md](../creation/encapsulate-composite-with-builder.md)).
- Leave small, stable trees implicit. Liability: it complicates the design when building the tree by hand is simpler. It is fine to start implicit and refactor when the code starts to bloat.

## Mechanics
Two paths work: apply refactorings to the existing code (Extract Class and friends), or grow the new classes test-first and then replace the old code. Use the second when the old code does not lend itself to extraction (for example, text built by concatenation).

1. Find an implicit leaf: a part of the tree that a class could represent. Create the leaf class, by [extract-class.md](../../fowler/encapsulation/extract-class.md) or test-first. If the leaf has attributes, give the class the same ones so its full representation matches the old output. Compile and test.
2. Replace each occurrence of the implicit leaf with an instance of the leaf class. Compile and test that the tree still behaves the same.
3. Repeat for every other kind of leaf. Give all leaf classes a common interface with [extract-superclass.md](../../fowler/inheritance/extract-superclass.md) or Extract Interface (1st ed. only; no link).
4. Find an implicit parent: a part that holds leaves. Create the parent class, by extraction or test-first. Clients add children through the constructor or an `Add` method, and the parent treats every child only through the common interface. Make the parent implement that interface too if parents must contain parents, or if clients should not care which kind of node they hold.
5. Replace each occurrence of the implicit parent with a parent instance holding the right leaves. Compile and test.
6. Repeat for the remaining implicit parents. Allow parents inside parents only if the implicit parents really behave alike.

## Example
Before: a report over a fixed two-level shape (categories of expenses) built with loops and hard-coded indentation. Adding a sub-category or changing the layout means touching this method.

```csharp
using System.Collections.Generic;
using System.Globalization;
using System.Text;

public static class ExpenseReport
{
    public static string Render(IReadOnlyDictionary<string, (string Item, decimal Amount)[]> categories)
    {
        var sb = new StringBuilder();
        decimal total = 0m;
        foreach (var (category, items) in categories)
        {
            sb.AppendLine(category);
            decimal subtotal = 0m;
            foreach (var (item, amount) in items)
            {
                sb.AppendLine($"  {item}: {Money(amount)}");
                subtotal += amount;
            }
            sb.AppendLine($"  subtotal: {Money(subtotal)}");
            total += subtotal;
        }
        sb.AppendLine($"total: {Money(total)}");
        return sb.ToString();
    }

    private static string Money(decimal value) => value.ToString("0.00", CultureInfo.InvariantCulture);
}
```

After: `Expense` is the leaf and `ExpenseGroup` the parent, both behind `IExpenseNode`. A group totals and indents its children itself, and a group can hold other groups, so a new level needs no change to the renderer. For the same two-level data the output is identical to the old method.

```csharp
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;

public interface IExpenseNode
{
    decimal Amount { get; }
    void Render(StringBuilder sb, int depth);
}

public record Expense(string Item, decimal Amount) : IExpenseNode
{
    public void Render(StringBuilder sb, int depth) =>
        sb.AppendLine($"{ExpenseReport.Indent(depth)}{Item}: {ExpenseReport.Money(Amount)}");
}

public class ExpenseGroup : IExpenseNode
{
    private readonly string _name;
    private readonly List<IExpenseNode> _children = new();

    public ExpenseGroup(string name, params IExpenseNode[] children)
    {
        _name = name;
        _children.AddRange(children);
    }

    public decimal Amount => _children.Sum(c => c.Amount);

    public void Add(IExpenseNode child) => _children.Add(child);

    public void Render(StringBuilder sb, int depth)
    {
        sb.AppendLine($"{ExpenseReport.Indent(depth)}{_name}");
        foreach (var child in _children)
            child.Render(sb, depth + 1);
        sb.AppendLine($"{ExpenseReport.Indent(depth + 1)}subtotal: {ExpenseReport.Money(Amount)}");
    }
}

public static class ExpenseReport
{
    public static string Render(IReadOnlyList<IExpenseNode> roots)
    {
        var sb = new StringBuilder();
        foreach (var root in roots)
            root.Render(sb, 0);
        sb.AppendLine($"total: {Money(roots.Sum(r => r.Amount))}");
        return sb.ToString();
    }

    public static string Indent(int depth) => new string(' ', depth * 2);

    public static string Money(decimal value) => value.ToString("0.00", CultureInfo.InvariantCulture);
}
```

The client now builds the tree, and nesting is just another `ExpenseGroup` inside a group:

```csharp
var travel = new ExpenseGroup("Travel",
    new Expense("Flight", 420m),
    new ExpenseGroup("Lodging", new Expense("Hotel", 310.5m)));
string text = ExpenseReport.Render(new IExpenseNode[] { travel });
```

## C# notes
- A `record` is a convenient leaf. An interface is enough for the common type unless leaves and parents share code.
- If the tree needs to be immutable, take the children in the constructor only and expose them as `IReadOnlyList<T>`; drop `Add`.
- Recursion depth is the tree depth. For very deep trees, check that no node renders by recursing unboundedly.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Keep a test that compares the old output with the new for the same data (the "golden" text), and run it after each step.
- Add one test with a nested parent, to prove the tree really composes.
