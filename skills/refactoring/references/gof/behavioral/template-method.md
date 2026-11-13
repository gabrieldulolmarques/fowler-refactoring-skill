# Template Method

Gamma et al. (1995), ch. 5, p. 325. Category: class behavioral.

## Intent
Write the skeleton of an algorithm once in a base class and leave some steps to subclasses. Subclasses fill in the steps without being able to change the order or structure of the whole.

## When it pays off
- The fixed part of an algorithm should live in one place, and only the varying parts should be written by subclasses.
- Subclasses repeat the same sequence of steps with different details. Find the differences, move each into its own method, and replace the duplicated sequence with one template method that calls them.
- You want to allow extension only at chosen points (hooks) and keep the rest closed.
- Benefits: reuse of the invariant part; the base class controls the flow ("don't call us, we'll call you"); a small, documented set of extension points.
- Liabilities: subclass authors must learn which methods to override; the design is tied to inheritance, so it is fixed at compile time and one base class per subclass; too many abstract steps make subclassing tedious.
- Skip it when the variation can be passed in as an object or delegate, or when there is only one implementation.

## Participants in C#
- **AbstractClass** (`ReportExporter`): defines the template method (`Export`, non-virtual) and the steps it calls. Abstract members are the steps a subclass must supply; virtual members with an empty or default body are the hooks.
- **ConcreteClass** (`CsvExporter`, `JsonExporter`): overrides the abstract steps and any hooks it needs.

## Example (C#)
A report export writes a list of sales rows as CSV or JSON. The order is always: header, rows with separators, footer. The format decides what each piece looks like.

```csharp
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

public class SaleRow
{
    public SaleRow(int id, string customer, decimal total)
    {
        Id = id;
        Customer = customer;
        Total = total;
    }

    public int Id { get; }
    public string Customer { get; }
    public decimal Total { get; }
}

public abstract class ReportExporter
{
    // Template method: fixed order, not overridable.
    public string Export(IReadOnlyList<SaleRow> rows)
    {
        if (rows is null) throw new ArgumentNullException(nameof(rows));

        var sb = new StringBuilder();
        WriteHeader(sb);
        for (int i = 0; i < rows.Count; i++)
        {
            if (i > 0) sb.Append(Separator);
            WriteRow(sb, rows[i]);
        }
        WriteFooter(sb);
        return sb.ToString();
    }

    // Primitive operation: every format must supply it.
    protected abstract void WriteRow(StringBuilder sb, SaleRow row);

    // Hooks: defaults that a format may replace.
    protected virtual string Separator => "";
    protected virtual void WriteHeader(StringBuilder sb) { }
    protected virtual void WriteFooter(StringBuilder sb) { }

    protected static string Money(decimal value) => value.ToString("0.00", CultureInfo.InvariantCulture);
}

public class CsvExporter : ReportExporter
{
    protected override string Separator => "\n";

    protected override void WriteHeader(StringBuilder sb) => sb.Append("id,customer,total\n");

    protected override void WriteRow(StringBuilder sb, SaleRow row) =>
        sb.Append(row.Id).Append(',').Append(Quote(row.Customer)).Append(',').Append(Money(row.Total));

    private static string Quote(string text) => "\"" + text.Replace("\"", "\"\"") + "\"";
}

public class JsonExporter : ReportExporter
{
    protected override string Separator => ",\n";

    protected override void WriteHeader(StringBuilder sb) => sb.Append("[\n");

    protected override void WriteFooter(StringBuilder sb) => sb.Append("\n]");

    protected override void WriteRow(StringBuilder sb, SaleRow row) =>
        sb.Append("  {\"id\":").Append(row.Id)
          .Append(",\"customer\":\"").Append(row.Customer.Replace("\\", "\\\\").Replace("\"", "\\\""))
          .Append("\",\"total\":").Append(Money(row.Total)).Append('}');
}

public static class Program
{
    public static void Main()
    {
        var rows = new List<SaleRow> { new(1, "Ana", 19.9m), new(2, "Bruno \"B\"", 5m) };

        foreach (ReportExporter exporter in new ReportExporter[] { new CsvExporter(), new JsonExporter() })
            Console.WriteLine(exporter.Export(rows));
    }
}
```

## Variations
- **Kinds of steps.** A template method may call concrete operations of its own class, helpers meant for subclasses (`Money`), abstract steps that must be overridden (`WriteRow`), factory methods that create parts, and hooks that may be overridden (`WriteHeader`).
- **Mark the difference.** Make clear which members must be overridden (abstract) and which may be (virtual, usually with an empty body). A naming prefix such as `Do` or `On` helps readers.
- **Few primitives.** Keep the number of abstract steps small. Every extra one is one more thing each subclass must write.
- **Protect the skeleton.** Leave the template method non-virtual, and make the steps `protected` so only the template calls them. This is how a base class enforces an invariant, such as "acquire a resource, run the step, always release it".
- **Turning an override into a hook.** If subclasses must call the base version of an override to be correct, change it into a template method with a hook, so the base class keeps control and subclasses cannot forget the call.

## Risks and C# alternatives
- If the variable steps are few, pass them as delegates or a small interface into one class (for example `Func<SaleRow, string>` for the row format, plus header and footer strings). That is Strategy: it can change at run time and needs no hierarchy.
- Inheritance couples subclasses to the base class's internals. Changing the order of steps or adding a call in the template can break subclasses that relied on the old order. Document the contract of each step.
- `virtual` members called from a base constructor run before the subclass constructor finishes. Do not call overridable steps from constructors.
- Async steps: make the steps return `Task` and the template `async`. A hook that is `async void` hides failures; return `Task`.
- Do not declare the template `virtual`. A subclass that overrides the template removes the guarantee the pattern gives. C# methods are non-virtual by default; use `sealed override` if an intermediate class inherits a template from above.

## Related patterns
- [Factory Method](../creational/factory-method.md): often called by template methods, as one of the steps.
- [Strategy](strategy.md): delegation instead of inheritance. A strategy replaces the whole algorithm; a template method replaces parts of it.

## Verification
- The order of steps appears in exactly one place, the template method, and no subclass reimplements it.
- Each subclass overrides only the abstract steps and the hooks it needs, and the file reads as "what is different about this format".
- Adding a new variant needs no change to the base class.
- Calling a step directly from outside is not possible (steps are `protected`), so the invariant cannot be skipped.
