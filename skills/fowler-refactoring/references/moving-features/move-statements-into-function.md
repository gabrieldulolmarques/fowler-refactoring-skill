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
Two methods print a customer's contact lines. Each one prints the customer name just before
calling `PrintContact`.

Before:

```csharp
using System.Collections.Generic;

public record Customer(string Name, string Email, string Phone);

public class StatementPrinter
{
    public IEnumerable<string> PrintInvoiceHeader(Customer customer)
    {
        var lines = new List<string> { "INVOICE" };
        lines.Add($"customer: {customer.Name}");
        lines.AddRange(PrintContact(customer));
        return lines;
    }

    public IEnumerable<string> PrintReminder(Customer customer)
    {
        var lines = new List<string> { "PAYMENT REMINDER" };
        lines.Add($"customer: {customer.Name}");
        lines.AddRange(PrintContact(customer));
        return lines;
    }

    private IEnumerable<string> PrintContact(Customer customer)
    {
        yield return $"email: {customer.Email}";
        yield return $"phone: {customer.Phone}";
    }
}
```

After step 3, `PrintInvoiceHeader` calls a temporary `PrintCustomerAndContact(customer)`, whose
body is the name line followed by the `PrintContact` call; `PrintReminder` still has its own name
line and `PrintContact` call. Steps 4 and 5 update `PrintReminder` and inline `PrintContact`, and
step 6 renames the temporary function to `PrintContact`. After:

```csharp
using System.Collections.Generic;

public record Customer(string Name, string Email, string Phone);

public class StatementPrinter
{
    public IEnumerable<string> PrintInvoiceHeader(Customer customer)
    {
        var lines = new List<string> { "INVOICE" };
        lines.AddRange(PrintContact(customer));
        return lines;
    }

    public IEnumerable<string> PrintReminder(Customer customer)
    {
        var lines = new List<string> { "PAYMENT REMINDER" };
        lines.AddRange(PrintContact(customer));
        return lines;
    }

    private IEnumerable<string> PrintContact(Customer customer)
    {
        yield return $"customer: {customer.Name}";
        yield return $"email: {customer.Email}";
        yield return $"phone: {customer.Phone}";
    }
}
```

The output of both methods is unchanged.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Search for the placeholder name to confirm it is gone.
- Confirm no caller still performs the moved statements itself.
- Compare the output of each caller before and after the change.
