# Return Modified Value

Fowler, online catalog: https://refactoring.com/catalog/returnModifiedValue.html (web edition only, no book section). Formerly / aka: —. Inverse: —.

## When to use
Smell: none specific (web catalog only; related: Mutable Data, Long Function).
- A function reads some inputs, computes a value and stores it in a variable declared outside it (a field, a local captured by the caller, a shared accumulator), returning nothing.
- A reader of the calling code cannot tell that the call produces a value, or which variable it feeds.
- You want to extract, move or reorder such code and the hidden write makes that risky.

Skip it when the function updates several variables at once (return a small record, or split the function first) or when mutating shared state is the whole point of the operation.

## Mechanics
The source page shows only a before/after code pair, so the smells, the skip condition and these steps are derived from that pair, not from published steps.

1. Identify the single outside variable the function updates, and every place that reads or writes it before and after the call.
2. Declare a local variable inside the function. Pick its starting value by case:
   - The function starts from a fixed value (the usual case, and the one in the example): start the local at that value.
   - The function accumulates onto a value left by earlier calls: start the local at the identity value (`0` for a sum, an empty collection for a list), and later have the caller combine the returned value with the outside variable.
3. Replace every write to the outside variable in the function body with a write to the local, and at the end of the function assign the local to the outside variable (combining it with the existing value in the accumulating case), so behavior stays the same. Compile and test.
4. Make the function return the local variable (change the return type from `void`). Compile and test.
5. At each call site, use the returned value in place of reading the outside variable (ideally assign it to a variable declared there, read-only if nothing else changes it). Compile and test.
6. Remove the final assignment to the outside variable from the function, and remove the outside variable if nothing else needs it. Rename the function if its name described an action rather than the value. Compile and test.

## Example
Before:

```csharp
public class InvoiceReport
{
    private decimal _totalDiscount;

    private void CalculateDiscount(IReadOnlyList<InvoiceLine> lines)
    {
        foreach (var line in lines)
        {
            if (line.Discount > 0)
                _totalDiscount += line.Discount;
        }
    }

    public decimal Summarize(IReadOnlyList<InvoiceLine> lines)
    {
        _totalDiscount = 0;
        CalculateDiscount(lines);
        return _totalDiscount;
    }
}

public record InvoiceLine(decimal Price, decimal Discount);
```

After:

```csharp
public class InvoiceReport
{
    private decimal CalculateDiscount(IReadOnlyList<InvoiceLine> lines)
    {
        var result = 0m;
        foreach (var line in lines)
        {
            if (line.Discount > 0)
                result += line.Discount;
        }
        return result;
    }

    public decimal Summarize(IReadOnlyList<InvoiceLine> lines)
    {
        return CalculateDiscount(lines);
    }
}

public record InvoiceLine(decimal Price, decimal Discount);
```

Same behavior, including repeated calls (the "before" resets the field at the start of `Summarize`), with the field gone and the data flow visible at the call.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
