# Visitor

Gamma et al. (1995), ch. 5, p. 331. Category: object behavioral.

## Intent
Package an operation over the elements of an object structure into a separate object, so you can add new operations without changing the element classes.

## When it pays off
- A structure holds many classes with different interfaces, and operations depend on the concrete class of each element.
- Many unrelated operations (pricing, rendering, auditing) would otherwise clutter the element classes. Each operation gets one visitor class that keeps its code and its working data together.
- The element classes rarely change, but new operations over them are added often.
- The structure is shared by many applications, and each application should get only the operations it needs.
- Benefits: a new operation is a new class; related code is in one place, unrelated code is apart; a visitor can accumulate state while it walks the structure; it can visit elements that share no common base class.
- Liabilities: adding a new element class is costly, because the visitor interface and every visitor must change; the elements usually have to expose enough of their state for visitors to work, which weakens encapsulation.
- Skip it when the element types change more often than the operations: put the operation on the elements instead.

## Participants in C#
- **Visitor** (`IInvoiceVisitor`): interface with one `Visit` method for each element class.
- **ConcreteVisitor** (`TotalCalculator`, `TextRenderer`): implements one operation over the whole structure, and keeps its running state in fields.
- **Element** (`InvoiceLine`): abstract class with `Accept(IInvoiceVisitor)`.
- **ConcreteElement** (`SubscriptionLine`, `UsageLine`, `DiscountLine`): implements `Accept` by calling the `Visit` method that matches its own type.
- **ObjectStructure** (`Invoice`): the collection of elements. It offers a way to hand a visitor to all of them.

## Example (C#)
A SaaS invoice is a list of lines of three kinds: a subscription fee, metered usage and a percentage discount. Totaling and rendering are two visitors. A third operation (a tax report, say) would be a new visitor, with no change to the lines.

```csharp
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

public interface IInvoiceVisitor
{
    void Visit(SubscriptionLine line);
    void Visit(UsageLine line);
    void Visit(DiscountLine line);
}

public abstract class InvoiceLine
{
    public abstract void Accept(IInvoiceVisitor visitor);
}

public sealed class SubscriptionLine : InvoiceLine
{
    public SubscriptionLine(string plan, decimal monthlyPrice)
    {
        Plan = plan;
        MonthlyPrice = monthlyPrice;
    }

    public string Plan { get; }
    public decimal MonthlyPrice { get; }

    public override void Accept(IInvoiceVisitor visitor) => visitor.Visit(this);   // first dispatch
}

public sealed class UsageLine : InvoiceLine
{
    public UsageLine(string metric, int units, decimal unitPrice)
    {
        Metric = metric;
        Units = units;
        UnitPrice = unitPrice;
    }

    public string Metric { get; }
    public int Units { get; }
    public decimal UnitPrice { get; }

    public override void Accept(IInvoiceVisitor visitor) => visitor.Visit(this);
}

public sealed class DiscountLine : InvoiceLine
{
    public DiscountLine(string label, decimal percent)
    {
        Label = label;
        Percent = percent;
    }

    public string Label { get; }
    public decimal Percent { get; }

    public override void Accept(IInvoiceVisitor visitor) => visitor.Visit(this);
}

public class Invoice
{
    private readonly List<InvoiceLine> _lines = new();

    public Invoice Add(InvoiceLine line)
    {
        _lines.Add(line);
        return this;
    }

    // The structure drives the traversal.
    public void Accept(IInvoiceVisitor visitor)
    {
        foreach (var line in _lines) line.Accept(visitor);
    }
}

public class TotalCalculator : IInvoiceVisitor
{
    public decimal Total { get; private set; }   // state accumulated during the walk

    public void Visit(SubscriptionLine line) => Total += line.MonthlyPrice;
    public void Visit(UsageLine line) => Total += line.Units * line.UnitPrice;
    public void Visit(DiscountLine line) => Total -= Total * line.Percent / 100m;   // applies to what came before
}

public class TextRenderer : IInvoiceVisitor
{
    private readonly StringBuilder _text = new();

    public string Text => _text.ToString();

    public void Visit(SubscriptionLine line) => _text.AppendLine($"{line.Plan} plan: {Money(line.MonthlyPrice)}");
    public void Visit(UsageLine line) => _text.AppendLine($"{line.Metric}: {line.Units} x {Money(line.UnitPrice)}");
    public void Visit(DiscountLine line) => _text.AppendLine($"{line.Label}: -{line.Percent}%");

    private static string Money(decimal value) => value.ToString("0.00", CultureInfo.InvariantCulture);
}

public static class Program
{
    public static void Main()
    {
        var invoice = new Invoice()
            .Add(new SubscriptionLine("Team", 40m))
            .Add(new UsageLine("api calls (thousands)", 25, 0.8m))
            .Add(new DiscountLine("Annual contract", 10m));

        var totals = new TotalCalculator();
        invoice.Accept(totals);

        var renderer = new TextRenderer();
        invoice.Accept(renderer);

        Console.Write(renderer.Text);
        Console.WriteLine($"Total: {totals.Total.ToString("0.00", CultureInfo.InvariantCulture)}");   // 54.00
    }
}
```

The same total with a `switch` on the element type, which needs no `Accept` or visitor interface:

```csharp
public static class PatternMatchingTotal
{
    public static decimal Of(IEnumerable<InvoiceLine> lines)
    {
        decimal total = 0;
        foreach (var line in lines)
        {
            switch (line)
            {
                case SubscriptionLine s: total += s.MonthlyPrice; break;
                case UsageLine u: total += u.Units * u.UnitPrice; break;
                case DiscountLine d: total -= total * d.Percent / 100m; break;
                default: throw new NotSupportedException(line.GetType().Name);
            }
        }
        return total;
    }
}
```

## Variations
- **Double dispatch.** The operation that runs depends on two types: the visitor's and the element's. `Accept` receives the visitor and calls the `Visit` overload for the element's own type, which is how the right code is selected without a type check. Languages with multiple dispatch need the pattern less.
- **Who walks the structure.** Most often the structure itself: a list calls `Accept` on each element, and a tree's `Accept` recurses into the children. A separate iterator is the other option, and so is the visitor, which suits an irregular walk or one that depends on earlier results, at the price of duplicating the walk in every visitor.
- **Overloads or distinct names.** `Visit(SubscriptionLine)` with overloads is short and shows the symmetry between the cases; names such as `VisitSubscription` make each call site explicit. Pick one and stay with it.
- **Default behavior.** An abstract base visitor can give each `Visit` an empty body, so a concrete visitor overrides only the element kinds it cares about.
- **Return values.** A generic `IInvoiceVisitor<TResult>` returns a result per element instead of accumulating it in a field, which makes the visitor reusable and removes the shared state.

## Risks and C# alternatives
- Pattern matching: `switch` statements and expressions over the element types do the same job in much less code when the set of element types is closed and lives in one assembly. The cost is that the compiler does not force every operation to handle a new element: without a failing `default` (as above), a new subclass is silently skipped. A visitor interface catches that at compile time, which is its main remaining advantage in C#.
- C# has `dynamic` dispatch (`visitor.Visit((dynamic)element)`), which removes `Accept` but costs speed and loses compile-time checking. Avoid it except in throwaway code.
- Every `Visit` signature changes when you add an element class. If elements change often, put the behavior on the elements.
- Visitors read element state, so properties that were private become public. Expose only what visitors need, as get-only members.
- A visitor with accumulated state (like `TotalCalculator`) can be used once. Create a new one for each walk, or reset it, and do not share one between threads.
- Deep structures walked recursively can overflow the stack; use an explicit stack in the traversal if depth is unbounded.

## Related patterns
- [Composite](../structural/composite.md): visitors apply an operation to a structure built as a composite.
- [Interpreter](interpreter.md): a visitor can carry out the interpretation over the syntax tree.
- [Iterator](iterator.md): can drive the traversal, but visits only elements that share a type; a visitor can handle unrelated element types.

## Verification
- A new operation over the structure is a new visitor class, and no element class changed.
- The element classes contain no operation-specific code (no pricing or formatting inside them).
- Adding an element class fails to compile until every visitor handles it, or the `switch` alternative has a failing default that a test exercises.
- Each visitor gives the same result when run on the same structure twice (state is reset or created per walk).
