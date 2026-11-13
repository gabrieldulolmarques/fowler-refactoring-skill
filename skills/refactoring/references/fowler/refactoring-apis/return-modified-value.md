# Return Modified Value

Fowler (2018), web edition only (not in the print book); summary at https://refactoring.com/catalog/returnModifiedValue.html. Formerly / aka: —. Inverse: —.

## When to use
Smell: none specific (web edition only; related: Mutable Data, Long Function).
- A function reads some inputs, computes a value and stores it in a variable declared outside it (a field, a local captured by the caller, a shared accumulator), returning nothing.
- A reader of the calling code cannot tell that the call produces a value, or which variable it feeds.
- You want to extract, move or reorder such code and the hidden write makes that risky.

Skip it when the function updates several variables at once (return a small record, or split the function first) or when mutating shared state is the whole point of the operation.

## Mechanics
1. Make the function return the variable it modifies, and at the call site assign the returned value to that variable. Compile and test.
2. Inside the function, declare a local for the value it returns, starting where the caller used to start it, and update the local instead of the outside variable. The caller's initialization is now ignored; changing it temporarily is a quick way to confirm that. Compile and test.
   - If the function accumulates onto a value left by earlier calls, start the local at the identity value (`0` for a sum, an empty list) and have the caller combine the result with its variable.
3. Combine the declaration with the calculation where you can, and make the receiving variable read-only if nothing else changes it. Compile and test.
4. Rename the variable inside the function to reflect its new role (often `result`), and remove the outside variable if nothing else needs it. Compile and test.

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
