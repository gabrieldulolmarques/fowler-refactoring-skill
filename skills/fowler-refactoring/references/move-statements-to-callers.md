# Move Statements to Callers

Fowler (2018), ch. 8, p. 217. Formerly / aka: —. Inverse: Move Statements into Function ([move-statements-into-function.md](move-statements-into-function.md)).

## When to use
- A function that was one cohesive unit now bundles two different things, and the abstraction boundary is in the wrong place.
- Behavior shared by several callers must now differ in one or more of them. Move the varying part out so each caller can change it freely.
- Typical preparation: use [slide-statements.md](slide-statements.md) to bring the varying statements to the start or end of the function, then move them to the callers.
- Not a fit when the boundary needs a complete redesign. In that case, inline the function ([inline-function.md](inline-function.md)), then slide and extract new functions to draw better boundaries.

## Mechanics
1. Simple case (one or two callers, a small function): cut the first or last statement from the function, paste it into each caller, adjust names or arguments as needed, build and test. You are done.
2. Otherwise, use [extract-function.md](extract-function.md) on the statements that are staying in the function. Give the extracted function a temporary name that is easy to search for. Build and test.
3. If the function is overridden in subclasses, extract the same remainder in every override until the remaining methods are identical, then delete the overrides and keep one.
4. Inline the original function ([inline-function.md](inline-function.md)) into one caller. Build and test. Repeat for each caller.
5. Delete the original function once no caller is left.
6. Give the extracted function its final name: the old name of the deleted function, or a clearer one if you have it ([change-function-declaration.md](change-function-declaration.md)). Build and test.

## Example
Before: `PrintInvoice` and `PrintReminder` both call `WriteSummary`, which ends with the due date. Reminders must show the due date differently.

```csharp
using System;
using System.IO;

public record Invoice(string Number, decimal Total, DateTime DueDate);

public static class InvoicePrinter
{
    public static void PrintInvoice(TextWriter output, Invoice invoice)
    {
        output.WriteLine("INVOICE");
        WriteSummary(output, invoice);
    }

    public static void PrintReminder(TextWriter output, Invoice invoice)
    {
        output.WriteLine("REMINDER");
        WriteSummary(output, invoice);
    }

    private static void WriteSummary(TextWriter output, Invoice invoice)
    {
        output.WriteLine($"Number: {invoice.Number}");
        output.WriteLine($"Total: {invoice.Total:C}");
        output.WriteLine($"Due: {invoice.DueDate:d}");
    }
}
```

Step 2: extract what stays (temporary name `ZzTmp`), then inline `WriteSummary` into each caller and delete it. Step 6: rename `ZzTmp` back to `WriteSummary`.

After: the due-date line now lives in the callers, and the reminder can change it.

```csharp
using System;
using System.IO;

public record Invoice(string Number, decimal Total, DateTime DueDate);

public static class InvoicePrinter
{
    public static void PrintInvoice(TextWriter output, Invoice invoice)
    {
        output.WriteLine("INVOICE");
        WriteSummary(output, invoice);
        output.WriteLine($"Due: {invoice.DueDate:d}");
    }

    public static void PrintReminder(TextWriter output, Invoice invoice)
    {
        output.WriteLine("REMINDER");
        WriteSummary(output, invoice);
        output.WriteLine($"Due: {invoice.DueDate:d}");
    }

    private static void WriteSummary(TextWriter output, Invoice invoice)
    {
        output.WriteLine($"Number: {invoice.Number}");
        output.WriteLine($"Total: {invoice.Total:C}");
    }
}
```

Behavior is unchanged at this point. The next change (a different due-date format in the reminder) now touches only `PrintReminder`.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
