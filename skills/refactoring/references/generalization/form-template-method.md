# Form Template Method

Kerievsky (2004), ch. 8, p. 205. Direction: to. Pattern: Template Method (GoF, p. 325).

## When to use
Smells: Duplicated Code.

- Two subclasses implement the same method, and both follow the same steps in the same order, but the steps themselves differ. The skeleton of the algorithm is copied into every subclass.
- Moving the skeleton into the superclass leaves each subclass with only the steps that really vary, and the order of the steps is stated once.
- Fowler's refactoring of the same name is the same idea; Kerievsky's version suits the case where the shared skeleton is hidden inside the bodies, not already visible as repeated statements.
- Do not use it when subclasses would have to implement many small methods just to fill in the skeleton: the hierarchy gets harder to read than the duplication it removed. Keep the number of abstract steps small and make optional steps concrete hooks.

## Mechanics
1. Find a similar method: two subclasses that run similar steps in a similar order. Apply Compose Method ([compose-method.md](../simplification/compose-method.md)) to it in both subclasses, so each step is a method. Steps with the same signature and body in both are identical methods; steps that differ are unique methods. When unsure which kind a step is, ask whether subclasses should inherit it (identical) or override it (unique).
2. Pull up the identical methods with Pull Up Method ([pull-up-method.md](../inheritance/pull-up-method.md)). Compile and test.
3. Make the similar method's body the same in both subclasses: rename each unique method so both subclasses call the same names, with Change Function Declaration ([change-function-declaration.md](../first-set/change-function-declaration.md)). Compile and test after each rename.
4. If the similar method's signature is not yet identical, change it the same way.
5. Pull up the similar method from one subclass and delete it from the other. Declare an abstract method in the superclass for every unique method (or a `virtual` one where a default makes sense). The pulled-up method is now the template. Compile and test.

## Example
Before: two exporters repeat the same sequence (header, one line per order, footer), each with its own formatting.

```csharp
using System.Collections.Generic;
using System.Text;

public record Order(string Id, string Customer, decimal Total);

public abstract class OrderExporter
{
    public abstract string Export(IReadOnlyList<Order> orders);
}

public class CsvOrderExporter : OrderExporter
{
    public override string Export(IReadOnlyList<Order> orders)
    {
        var sb = new StringBuilder();
        sb.AppendLine("id,customer,total");
        foreach (var o in orders)
            sb.AppendLine($"{o.Id},{o.Customer},{o.Total}");
        sb.AppendLine($"count={orders.Count}");
        return sb.ToString();
    }
}

public class TextOrderExporter : OrderExporter
{
    public override string Export(IReadOnlyList<Order> orders)
    {
        var sb = new StringBuilder();
        sb.AppendLine("ORDERS");
        foreach (var o in orders)
            sb.AppendLine($"{o.Id} for {o.Customer}: {o.Total}");
        sb.AppendLine($"count={orders.Count}");
        return sb.ToString();
    }
}
```

After: the superclass owns the sequence and the identical footer. Each subclass writes only its header and its row.

```csharp
using System.Collections.Generic;
using System.Text;

public record Order(string Id, string Customer, decimal Total);

public abstract class OrderExporter
{
    public string Export(IReadOnlyList<Order> orders)
    {
        var sb = new StringBuilder();
        WriteHeader(sb);
        foreach (var o in orders)
            WriteRow(sb, o);
        WriteFooter(sb, orders.Count);
        return sb.ToString();
    }

    protected abstract void WriteHeader(StringBuilder sb);
    protected abstract void WriteRow(StringBuilder sb, Order order);
    protected virtual void WriteFooter(StringBuilder sb, int count) => sb.AppendLine($"count={count}");
}

public class CsvOrderExporter : OrderExporter
{
    protected override void WriteHeader(StringBuilder sb) => sb.AppendLine("id,customer,total");
    protected override void WriteRow(StringBuilder sb, Order o) => sb.AppendLine($"{o.Id},{o.Customer},{o.Total}");
}

public class TextOrderExporter : OrderExporter
{
    protected override void WriteHeader(StringBuilder sb) => sb.AppendLine("ORDERS");
    protected override void WriteRow(StringBuilder sb, Order o) => sb.AppendLine($"{o.Id} for {o.Customer}: {o.Total}");
}
```

## C# notes
- `Export` is not `virtual`, so a subclass cannot replace the sequence by accident. A method that was never virtual is the C# equivalent of Java's `final` template.
- Mark required steps `abstract` and optional ones `virtual` with a useful default (the footer above). Use `protected` for both, since callers should only see the template.
- If the variation is one or two small steps, passing delegates or a strategy object into a single method is often lighter than a hierarchy.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Each subclass's output is byte-for-byte the same as before (compare the strings in a test), including the order of the steps.
