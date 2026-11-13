# Move Statements into Function

Fowler (2018), ch. 8, p. 213. Formerly / aka: —. Inverse: Move Statements to Callers
([move-statements-to-callers.md](move-statements-to-callers.md)).

## When to use
- Every call to a function is accompanied by the same statements, right before or right after it.
- Those statements are easier to understand as part of the function than as something each
  caller must remember to do.
- Moving them means a future change happens in one place instead of one per caller.

Skip it when the statements do not really belong to the function but must still run with it.
In that case extract a new function that wraps the statements and the call (the same steps
below, minus the inline and rename). Also skip it when callers already differ, or are likely to;
if a shared behavior has to start varying, the inverse refactoring is the tool.

## Mechanics
1. Make sure the statements sit directly next to the call; if not, use Slide Statements
   ([slide-statements.md](slide-statements.md)) to bring them together.
2. With a single caller, just cut the statements into the function body, run the tests and stop.
3. With several callers, pick one and apply Extract Function
   ([extract-function.md](../first-set/extract-function.md)) to the statements together with the call. Give
   the new function a placeholder name you can search for later.
4. Replace the statements and the old call in each other caller with a call to the new function,
   running the tests after each replacement.
5. When no caller uses the original function any more, apply Inline Function
   ([inline-function.md](../first-set/inline-function.md)) to fold it into the new one, then delete it.
6. Use Change Function Declaration
   ([change-function-declaration.md](../first-set/change-function-declaration.md)) to rename the new function
   to the original name, or a better one.

## Example
Two methods print a shipment's address block. Each one prints the recipient name just before
calling `PrintAddress`.

Before:

```csharp
using System.Collections.Generic;

public class Recipient
{
    public Recipient(string name, string street, string city)
    {
        Name = name;
        Street = street;
        City = city;
    }

    public string Name { get; }
    public string Street { get; }
    public string City { get; }
}

public class LabelPrinter
{
    public IEnumerable<string> PrintShippingLabel(Recipient recipient)
    {
        var lines = new List<string> { "SHIPPING LABEL" };
        lines.Add($"recipient: {recipient.Name}");
        lines.AddRange(PrintAddress(recipient));
        return lines;
    }

    public IEnumerable<string> PrintDeliveryReceipt(Recipient recipient)
    {
        var lines = new List<string> { "DELIVERY RECEIPT" };
        lines.Add($"recipient: {recipient.Name}");
        lines.AddRange(PrintAddress(recipient));
        return lines;
    }

    private IEnumerable<string> PrintAddress(Recipient recipient)
    {
        yield return $"street: {recipient.Street}";
        yield return $"city: {recipient.City}";
    }
}
```

After step 3, `PrintShippingLabel` calls a temporary `PrintRecipientAndAddress(recipient)`, whose
body is the name line followed by the `PrintAddress` call; `PrintDeliveryReceipt` still has its own name
line and `PrintAddress` call. Steps 4 and 5 update `PrintDeliveryReceipt` and inline `PrintAddress`, and
step 6 renames the temporary function to `PrintAddress`. After:

```csharp
using System.Collections.Generic;

public class LabelPrinter
{
    public IEnumerable<string> PrintShippingLabel(Recipient recipient)
    {
        var lines = new List<string> { "SHIPPING LABEL" };
        lines.AddRange(PrintAddress(recipient));
        return lines;
    }

    public IEnumerable<string> PrintDeliveryReceipt(Recipient recipient)
    {
        var lines = new List<string> { "DELIVERY RECEIPT" };
        lines.AddRange(PrintAddress(recipient));
        return lines;
    }

    private IEnumerable<string> PrintAddress(Recipient recipient)
    {
        yield return $"recipient: {recipient.Name}";
        yield return $"street: {recipient.Street}";
        yield return $"city: {recipient.City}";
    }
}
```

The output of both methods is unchanged.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Search for the placeholder name to confirm it is gone.
- Confirm no caller still performs the moved statements itself.
- Compare the output of each caller before and after the change.
