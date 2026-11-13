# Extract Parameter

Kerievsky (2004), ch. 11, p. 346. Pattern: —. Direction: —.

## When to use
Smells: — (a low-level step; the book needed it right after turning inheritance into delegation).

- A field is assigned from an object created inside the class (in a constructor or method), and you would rather let the client decide which object it gets.
- Split the assignment in two: the client supplies the right-hand side, the class keeps the left-hand side.
- The book used it in [move-embellishment-to-decorator.md](../simplification/move-embellishment-to-decorator.md), after Replace Superclass with Delegate ([replace-superclass-with-delegate.md](../../fowler/inheritance/replace-superclass-with-delegate.md)): the class that delegates created its own delegate, but a client needed to supply it.

## Mechanics
1. The assignment must be in a constructor or method. If it is not (a field initializer, for example), move it into one first.
2. Add a parameter for the value ([change-function-declaration.md](../../fowler/first-set/change-function-declaration.md)), typed as the field's type. Pass at each call site the expression that used to sit in the assignment, and change the assignment to use the parameter. Compile and test.
3. If the old arguments of the method are no longer used, remove them with Change Function Declaration too.

## Example
Before: the exporter creates its own CSV formatter, so a different format means editing the class.

```csharp
public interface IFormatter { string Format(string name, decimal total); }

public class CsvFormatter : IFormatter
{
    public string Format(string name, decimal total) => $"{name},{total:F2}";
}

public class OrderExporter
{
    private readonly IFormatter _formatter;

    public OrderExporter() => _formatter = new CsvFormatter();

    public string Export(string name, decimal total) => _formatter.Format(name, total);
}
```

After: the formatter comes from the client. The old behavior lives in the call site that builds the exporter.

```csharp
public class OrderExporter
{
    private readonly IFormatter _formatter;

    public OrderExporter(IFormatter formatter) => _formatter = formatter;

    public string Export(string name, decimal total) => _formatter.Format(name, total);
}

public static class Caller
{
    public static OrderExporter Make() => new(new CsvFormatter());
}
```

## C# notes
- Validate at the boundary: a `null` parameter should fail with `ArgumentNullException.ThrowIfNull(formatter)` where a null would otherwise show up much later.
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- No code in the class creates the value any more, and a test can now pass in a fake of the type.
