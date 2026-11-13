# Move Accumulation to Collecting Parameter

Kerievsky (2004), ch. 10, p. 313. Pattern: Collecting Parameter. Direction: to.

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
2. Pick one accumulation step and apply Extract Function ([extract-function.md](../../fowler/first-set/extract-function.md)) to move it into a private method that returns `void` and receives the result as a parameter, writing into it there. Compile and test.
3. Repeat step 2 for every step. The original method should now only create the result, pass it to the extracted methods, and read the final value. Compile and test.

**Beyond the book:** when a step also produces a value the caller needs (a subtotal, for example), the extracted method may return that value as well. The result being built still goes through the parameter.

## Example
Before: one method builds the CSV text, concatenating onto a string while it also computes the total.

```csharp
using System.Collections.Generic;

public class ExportRow
{
    public string Id { get; }
    public string Label { get; }
    public decimal Amount { get; }

    public ExportRow(string id, string label, decimal amount)
    {
        Id = id;
        Label = label;
        Amount = amount;
    }
}

public class ExportBatch
{
    public string Name { get; }
    public IReadOnlyList<ExportRow> Rows { get; }
    public decimal Fee { get; }

    public ExportBatch(string name, IReadOnlyList<ExportRow> rows, decimal fee)
    {
        Name = name;
        Rows = rows;
        Fee = fee;
    }
}

public class CsvExporter
{
    public string Export(ExportBatch batch)
    {
        var text = "";
        text += $"# {batch.Name}\n";
        text += "id,label,amount\n";
        decimal total = 0m;
        foreach (var row in batch.Rows)
        {
            text += $"{row.Id},{row.Label},{row.Amount:F2}\n";
            total += row.Amount;
        }
        if (batch.Fee > 0m)
        {
            text += $"fee,,-{batch.Fee:F2}\n";
            total -= batch.Fee;
        }
        text += $"total,,{total:F2}\n";
        return text;
    }
}
```

After: the `StringBuilder` is created once and passed to each step. The steps that also contribute to the total return an amount, which departs from the book's `void` rule in step 2 (see the note after the mechanics).

```csharp
using System.Text;

public class CsvExporter
{
    public string Export(ExportBatch batch)
    {
        var text = new StringBuilder();
        WriteHeader(batch, text);
        var total = WriteRows(batch, text);
        total -= WriteFee(batch, text);
        text.Append($"total,,{total:F2}\n");
        return text.ToString();
    }

    private static void WriteHeader(ExportBatch batch, StringBuilder text)
    {
        text.Append($"# {batch.Name}\n");
        text.Append("id,label,amount\n");
    }

    private static decimal WriteRows(ExportBatch batch, StringBuilder text)
    {
        decimal total = 0m;
        foreach (var row in batch.Rows)
        {
            text.Append($"{row.Id},{row.Label},{row.Amount:F2}\n");
            total += row.Amount;
        }
        return total;
    }

    private static decimal WriteFee(ExportBatch batch, StringBuilder text)
    {
        if (batch.Fee <= 0m) return 0m;
        text.Append($"fee,,-{batch.Fee:F2}\n");
        return batch.Fee;
    }
}
```

## C# notes
- `string` is immutable, so step 1 usually means `StringBuilder`. For lists, an `ICollection<T>` or `List<T>` passed in works the same way.
- Where the parameter only ever receives text, a `TextWriter` parameter lets callers pick the destination (a string, a file, a stream) and avoids a final `ToString()`.
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The output is byte-for-byte the same as before for a few representative inputs, including the empty and the with-fee cases.
