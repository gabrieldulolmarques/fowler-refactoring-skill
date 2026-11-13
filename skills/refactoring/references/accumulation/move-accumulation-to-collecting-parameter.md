# Move Accumulation to Collecting Parameter

Kerievsky (2004), ch. 10, p. 313. Direction: to. Pattern: Collecting Parameter (not in GoF; the book credits Kent Beck, Smalltalk Best Practice Patterns).

## When to use
Smells: Long Method.

- One bulky method builds up a result in a local variable (a string, a list, a running report). To split it into small methods, each piece needs somewhere to put what it finds.
- Instead of each extracted method returning a piece that the caller must combine, pass the result object to each of them and let them add to it. The object that gathers the data is the Collecting Parameter.
- It pairs naturally with [compose-method.md](../simplification/compose-method.md): the accumulation method ends up as three things, create the result, pass it along, read it back.
- It also works across several objects, for example recursively over a Composite: each node adds its own data to the same parameter.
- Benefits: smaller, simpler methods, and sometimes faster code (one buffer instead of many concatenations).
- Limit: it suits specific classes with a known interface. When the data comes from many unrelated classes with different interfaces, [move-accumulation-to-visitor.md](move-accumulation-to-visitor.md) can be cleaner, but try this one first because a Visitor is harder to build.

## Mechanics
1. Find the accumulation method and the local variable that holds the result. If its type cannot be built up across calls (an immutable string, for example), change it to one that can, such as a `StringBuilder`. Compile.
2. Pick one accumulation step and apply Extract Function ([extract-function.md](../first-set/extract-function.md)) to move it into a private method that returns `void` and receives the result as a parameter, writing into it there. Compile and test.
3. Repeat step 2 for every step. The original method should now only create the result, pass it to the extracted methods, and read the final value. Compile and test.

When a step also produces a value the caller needs (a subtotal, for example), the extracted method may return that value as well. The result being built still goes through the parameter.

## Example
Before: one method builds the text, concatenating onto a string while it also computes the total.

```csharp
public record Line(string Sku, int Qty, decimal UnitPrice);
public record Invoice(string Number, string Customer, IReadOnlyList<Line> Lines, decimal Discount);

public class InvoiceRenderer
{
    public string Render(Invoice invoice)
    {
        var text = "";
        text += $"Invoice {invoice.Number}\n";
        text += $"Customer: {invoice.Customer}\n";
        decimal total = 0m;
        foreach (var line in invoice.Lines)
        {
            var amount = line.Qty * line.UnitPrice;
            text += $"{line.Sku} x{line.Qty} = {amount:F2}\n";
            total += amount;
        }
        if (invoice.Discount > 0m)
        {
            text += $"Discount: -{invoice.Discount:F2}\n";
            total -= invoice.Discount;
        }
        text += $"Total: {total:F2}\n";
        return text;
    }
}
```

After: the `StringBuilder` is created once and passed to each step. The steps that also contribute to the total return an amount.

```csharp
using System.Text;

public class InvoiceRenderer
{
    public string Render(Invoice invoice)
    {
        var text = new StringBuilder();
        WriteHeader(invoice, text);
        var total = WriteLines(invoice, text);
        total -= WriteDiscount(invoice, text);
        text.Append($"Total: {total:F2}\n");
        return text.ToString();
    }

    private static void WriteHeader(Invoice invoice, StringBuilder text)
    {
        text.Append($"Invoice {invoice.Number}\n");
        text.Append($"Customer: {invoice.Customer}\n");
    }

    private static decimal WriteLines(Invoice invoice, StringBuilder text)
    {
        decimal total = 0m;
        foreach (var line in invoice.Lines)
        {
            var amount = line.Qty * line.UnitPrice;
            text.Append($"{line.Sku} x{line.Qty} = {amount:F2}\n");
            total += amount;
        }
        return total;
    }

    private static decimal WriteDiscount(Invoice invoice, StringBuilder text)
    {
        if (invoice.Discount <= 0m) return 0m;
        text.Append($"Discount: -{invoice.Discount:F2}\n");
        return invoice.Discount;
    }
}
```

## C# notes
- `string` is immutable, so step 1 usually means `StringBuilder`. For lists, an `ICollection<T>` or `List<T>` passed in works the same way.
- Where the parameter only ever receives text, a `TextWriter` parameter lets callers pick the destination (a string, a file, a stream) and avoids a final `ToString()`.
- A method that adds to its parameter has a side effect; name the extracted methods `Write...` or `Append...` so that is visible.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The output is byte-for-byte the same as before for a few representative inputs, including the empty and the discounted cases.
