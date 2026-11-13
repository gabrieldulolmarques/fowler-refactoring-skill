# Split Phase

Fowler (2018), ch. 6, p. 154. Formerly / aka: —. Inverse: —.

## When to use

Smells: Divergent Change, Shotgun Surgery.

- A fragment does two different things in sequence, and the output of the first is the input of the second: parse then compute, compute then format, validate then execute.
- The inputs do not match the model the main logic needs, so the logic is cluttered with conversion work.
- If the first lines and the last lines touch unrelated variables and helper calls, they are probably two phases.
- Worth it when changes are coming to either concern. If the two parts will never change independently, a plain Extract Function may be enough.
- The phases can be functions, or larger modules. A phase may also be a small object (for example a transformer) instead of a function.

## Mechanics

1. Extract the code of the second phase into its own function ([extract-function.md](extract-function.md)). Pass whatever it needs as plain parameters for now, even if the list is long.
2. Compile and test.
3. Create the intermediate data structure and pass it to the extracted function as an extra parameter. At this point it can be empty.
4. Compile and test.
5. Go through the second-phase parameters one at a time. If the first phase produces or uses a parameter, store it as a field of the intermediate structure, read it from there in the second phase and drop the parameter. Compile and test after each move.
   - If a parameter should not be known to the second phase at all, compute the value it feeds in the first phase, store the result in a field, and move the line that fills it back to the caller ([move-statements-to-callers.md](../moving-features/move-statements-to-callers.md)).
   - Parameters used only by the second phase stay as parameters.
6. What remains in the original function is now the first phase. Turn it into a function of its own whose result is the intermediate structure ([extract-function.md](extract-function.md)), then compile and test. If the first phase grows helpers that share its inputs, it can be an object instead (a transformer) whose method returns the intermediate structure; see the variation below.
7. Optionally tidy: inline leftover temporaries in the orchestrating function so it reads as "run phase one, feed phase two".

## Example

Before: one method both computes the totals and renders the text.

```csharp
using System.Collections.Generic;
using System.Text;

public class CartLine
{
    public string Sku { get; }
    public int Quantity { get; }
    public decimal UnitPrice { get; }

    public CartLine(string sku, int quantity, decimal unitPrice)
    {
        Sku = sku;
        Quantity = quantity;
        UnitPrice = unitPrice;
    }
}

public class CheckoutSummary
{
    public string Summary(IReadOnlyList<CartLine> lines, decimal taxRate, string currencySymbol)
    {
        decimal subtotal = 0m;
        foreach (var line in lines)
        {
            subtotal += line.Quantity * line.UnitPrice;
        }
        decimal tax = subtotal * taxRate;
        decimal shipping = subtotal >= 50m ? 0m : 4.90m;

        var sb = new StringBuilder();
        sb.AppendLine($"Items: {lines.Count}");
        sb.AppendLine($"Subtotal: {currencySymbol}{subtotal:F2}");
        sb.AppendLine($"Tax: {currencySymbol}{tax:F2}");
        sb.AppendLine($"Shipping: {currencySymbol}{shipping:F2}");
        return sb.ToString();
    }
}
```

After: totals and rendering are separate phases, linked by a `CartTotals` object.

```csharp
using System.Collections.Generic;
using System.Text;

public class CartTotals
{
    public int ItemCount { get; }
    public decimal Subtotal { get; }
    public decimal Tax { get; }
    public decimal Shipping { get; }

    public CartTotals(int itemCount, decimal subtotal, decimal tax, decimal shipping)
    {
        ItemCount = itemCount;
        Subtotal = subtotal;
        Tax = tax;
        Shipping = shipping;
    }
}

public class CheckoutSummary
{
    public string Summary(IReadOnlyList<CartLine> lines, decimal taxRate, string currencySymbol)
    {
        var totals = ComputeTotals(lines, taxRate);
        return Render(totals, currencySymbol);
    }

    private static CartTotals ComputeTotals(IReadOnlyList<CartLine> lines, decimal taxRate)
    {
        decimal subtotal = 0m;
        foreach (var line in lines)
        {
            subtotal += line.Quantity * line.UnitPrice;
        }
        decimal tax = subtotal * taxRate;
        decimal shipping = subtotal >= 50m ? 0m : 4.90m;
        return new CartTotals(lines.Count, subtotal, tax, shipping);
    }

    private static string Render(CartTotals totals, string currencySymbol)
    {
        var sb = new StringBuilder();
        sb.AppendLine($"Items: {totals.ItemCount}");
        sb.AppendLine($"Subtotal: {currencySymbol}{totals.Subtotal:F2}");
        sb.AppendLine($"Tax: {currencySymbol}{totals.Tax:F2}");
        sb.AppendLine($"Shipping: {currencySymbol}{totals.Shipping:F2}");
        return sb.ToString();
    }
}
```

Same output for the same input. Now a new output format touches only `Render`, and a new total touches `ComputeTotals` plus the fields it feeds.

### Variation: the first phase as a transformer object

When the first phase needs several helpers over the same input, a small class keeps them together. The class takes the raw input, and one method returns the intermediate structure. `Render` does not change.

```csharp
using System.Collections.Generic;
using System.Linq;
using System.Text;

public class CartTotals
{
    public int ItemCount { get; }
    public decimal Subtotal { get; }
    public decimal Tax { get; }
    public decimal Shipping { get; }

    public CartTotals(int itemCount, decimal subtotal, decimal tax, decimal shipping)
    {
        ItemCount = itemCount;
        Subtotal = subtotal;
        Tax = tax;
        Shipping = shipping;
    }
}

public class CartTotalsCalculator
{
    private readonly IReadOnlyList<CartLine> _lines;
    private readonly decimal _taxRate;

    public CartTotalsCalculator(IReadOnlyList<CartLine> lines, decimal taxRate)
    {
        _lines = lines;
        _taxRate = taxRate;
    }

    public CartTotals Run()
    {
        var subtotal = Subtotal();
        return new(_lines.Count, subtotal, subtotal * _taxRate, ShippingFor(subtotal));
    }

    private decimal Subtotal() => _lines.Sum(l => l.Quantity * l.UnitPrice);

    private static decimal ShippingFor(decimal subtotal) => subtotal >= 50m ? 0m : 4.90m;
}

public class CheckoutSummary
{
    public string Summary(IReadOnlyList<CartLine> lines, decimal taxRate, string currencySymbol)
    {
        var totals = new CartTotalsCalculator(lines, taxRate).Run();
        return Render(totals, currencySymbol);
    }

    private static string Render(CartTotals totals, string currencySymbol)
    {
        var sb = new StringBuilder();
        sb.AppendLine($"Items: {totals.ItemCount}");
        sb.AppendLine($"Subtotal: {currencySymbol}{totals.Subtotal:F2}");
        sb.AppendLine($"Tax: {currencySymbol}{totals.Tax:F2}");
        sb.AppendLine($"Shipping: {currencySymbol}{totals.Shipping:F2}");
        return sb.ToString();
    }
}
```

Same output as before, including an empty cart (shipping is still `4.90`, as in the original).

## C# notes

- The intermediate data structure is usually a `record` (or a `readonly record struct` for small, hot data; C# 9+, and on Unity it needs an `IsExternalInit` shim). Immutability keeps the phases from reaching into each other's state.

## Verification

- Compiles and the tests pass after every step; one commit per refactoring.
- Behavior is unchanged: same output for the same input, including edge cases such as empty input.
- The second phase no longer reads anything that only the first phase should know; its parameters are the intermediate structure plus data it genuinely owns.
