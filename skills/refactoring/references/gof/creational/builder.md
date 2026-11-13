# Builder

Gamma et al. (1995), ch. 3, p. 97. Category: object creational.

## Intent
Separate the step-by-step process of assembling a complex object from the representation that results, so the same process can produce different representations.

## When it pays off
- The procedure that decides which parts to create and in what order should be reusable and independent of what the parts are and how they are put together.
- The same procedure must be able to produce different outputs (CSV and JSON of the same report, for instance).
- Construction is a sequence of steps, and the product is only complete at the end; the builder gives finer control over that process than a single constructor call.
- It keeps the code that builds a representation in one place, apart from the code that decides what to build.
- Not worth it when a constructor with a few parameters, or an object initializer, already reads well. Builders earn their place with many optional parts or several output forms.

## Participants in C#
- **Builder** (`IReportBuilder`): interface with one method per construction step.
- **ConcreteBuilder** (`CsvReportBuilder`, `JsonReportBuilder`): implements the steps, accumulates the result, and exposes a method to retrieve it.
- **Director** (`ReportDirector`): runs the construction steps against whatever builder it receives.
- **Product** (`string` here, but it can be any class): the finished object. Different builders often return unrelated types, so a common product interface is not required.

## Example (C#)
A report export must be producible as CSV or JSON from the same rows. The director decides the order (title, then rows); each builder decides the format.

```csharp
using System.Collections.Generic;
using System.Globalization;
using System.Text;

public interface IReportBuilder
{
    void AddTitle(string title);
    void AddRow(string label, decimal value);
}

public class CsvReportBuilder : IReportBuilder
{
    private readonly StringBuilder _text = new();

    public void AddTitle(string title) => _text.AppendLine("# " + title);

    public void AddRow(string label, decimal value) =>
        _text.AppendLine(label + "," + value.ToString(CultureInfo.InvariantCulture));

    public string GetResult() => _text.ToString();
}

public class JsonReportBuilder : IReportBuilder
{
    private string _title = "";
    private readonly List<string> _rows = new();

    public void AddTitle(string title) => _title = title;

    public void AddRow(string label, decimal value) =>
        _rows.Add("{\"label\":\"" + label.Replace("\"", "\\\"") + "\",\"value\":" +
                  value.ToString(CultureInfo.InvariantCulture) + "}");

    public string GetResult() =>
        "{\"title\":\"" + _title.Replace("\"", "\\\"") + "\",\"rows\":[" + string.Join(",", _rows) + "]}";
}

public class ReportDirector
{
    public void Construct(IReportBuilder builder, string title, IEnumerable<(string Label, decimal Value)> rows)
    {
        builder.AddTitle(title);
        foreach (var (label, value) in rows)
            builder.AddRow(label, value);
    }
}

public static class Program
{
    public static void Main()
    {
        var rows = new List<(string Label, decimal Value)> { ("Subscriptions", 1200m), ("Refunds", -80.5m) };
        var director = new ReportDirector();

        var csv = new CsvReportBuilder();
        director.Construct(csv, "Monthly revenue", rows);
        System.Console.WriteLine(csv.GetResult());

        var json = new JsonReportBuilder();
        director.Construct(json, "Monthly revenue", rows);
        System.Console.WriteLine(json.GetResult());
    }
}
```

A second form is common in C#: a fluent builder with no director, where the caller issues the steps and the final call produces an immutable object. It suits objects with many optional settings.

```csharp
using System;

public class RetryPolicy
{
    public int MaxAttempts { get; }
    public TimeSpan Delay { get; }
    public bool Exponential { get; }

    public RetryPolicy(int maxAttempts, TimeSpan delay, bool exponential)
    {
        MaxAttempts = maxAttempts;
        Delay = delay;
        Exponential = exponential;
    }
}

public class RetryPolicyBuilder
{
    private int _maxAttempts = 3;
    private TimeSpan _delay = TimeSpan.FromMilliseconds(200);
    private bool _exponential;

    public RetryPolicyBuilder Attempts(int count) { _maxAttempts = count; return this; }
    public RetryPolicyBuilder WaitingBetween(TimeSpan delay) { _delay = delay; return this; }
    public RetryPolicyBuilder WithExponentialBackoff() { _exponential = true; return this; }

    public RetryPolicy Build()
    {
        if (_maxAttempts < 1) throw new InvalidOperationException("At least one attempt is required.");
        return new RetryPolicy(_maxAttempts, _delay, _exponential);
    }
}
```

## Variations
- **Empty defaults in the builder interface.** In the book's form the builder base class implements every step as a no-op, so a concrete builder overrides only what it needs. In C#, use an abstract class with `virtual` empty methods, or default interface methods (C# 8), instead of forcing every builder to implement all steps.
- **Appending versus querying earlier parts.** Most builders only append. If a step needs a part built earlier (a link between two existing nodes), the builder must expose a way to look it up, or return handles from earlier steps that the director passes back.
- **No common product type.** Because outputs can be unrelated, `GetResult()` is declared on each concrete builder, and the client that chose the builder knows its type. Forcing a shared product base class usually buys nothing.
- **Fluent builder without director.** The step order is up to the caller; `Build()` validates and returns an immutable object.

## Risks and C# alternatives
- For plain "many optional parameters", named and optional arguments, or an object initializer with get/set properties, are simpler than a builder class.
- A fluent builder that is reused after `Build()` shares mutable state with the next product. Either make `Build()` copy the collections it holds or document the builder as single use.
- Validate in `Build()` (or in the product's constructor), not in each step, so an incomplete object cannot escape.
- For string output, `StringBuilder` already is a builder; do not wrap it unless a second representation is really needed.
- With dependency injection, builders that hold per-call state should be registered as transient, never as a singleton.

## Related patterns
- [Abstract Factory](abstract-factory.md): similar goal, but it returns each product immediately and focuses on families, while Builder constructs one complex product step by step.
- [Composite](../structural/composite.md): the structure a builder frequently assembles.

## Verification
- The director contains no format-specific code, and builders contain no ordering logic.
- Adding a third output format needs one new builder and no change to the director.
- The same input through two builders yields equivalent content in two forms (covered by a test per builder).
- An incomplete or invalid build fails at `Build()`/`GetResult()` instead of producing a half-made product.
