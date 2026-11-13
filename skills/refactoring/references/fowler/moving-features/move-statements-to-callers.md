# Move Statements to Callers

Fowler (2018), ch. 8, p. 217. Formerly / aka: —. Inverse: Move Statements into Function ([move-statements-into-function.md](move-statements-into-function.md)).

## When to use
- A function that was one cohesive unit now bundles two different things, and the abstraction boundary is in the wrong place.
- Behavior shared by several callers must now differ in one or more of them. Move the varying part out so each caller can change it freely.
- Typical preparation: use [slide-statements.md](slide-statements.md) to bring the varying statements to the start or end of the function, then move them to the callers.
- Not a fit when the boundary needs a complete redesign. In that case, inline the function ([inline-function.md](../first-set/inline-function.md)), then slide and extract new functions to draw better boundaries.

## Mechanics
1. Simple case (one or two callers, a small function): cut the first or last statement from the function, paste it into each caller, adjust names or arguments as needed, build and test. You are done.
2. Otherwise, use [extract-function.md](../first-set/extract-function.md) on the statements that are staying in the function. Give the extracted function a temporary name that is easy to search for. Build and test.
3. If the function is overridden in subclasses, extract the same remainder in every override until the remaining methods are identical, then delete the overrides and keep one.
4. Inline the original function ([inline-function.md](../first-set/inline-function.md)) into one caller. Build and test. Repeat for each caller.
5. Delete the original function once no caller is left.
6. Give the extracted function its final name: the old name of the deleted function, or a clearer one if you have it ([change-function-declaration.md](../first-set/change-function-declaration.md)). Build and test.

## Example
Before: `PrintReceipt` and `PrintDelayNotice` both call `WriteSummary`, which ends with the estimated arrival. The delay notice must show the arrival differently.

```csharp
using System;
using System.IO;

public class Shipment
{
    public Shipment(string trackingCode, string carrier, DateTime eta)
    {
        TrackingCode = trackingCode;
        Carrier = carrier;
        Eta = eta;
    }

    public string TrackingCode { get; }
    public string Carrier { get; }
    public DateTime Eta { get; }
}

public static class ShipmentPrinter
{
    public static void PrintReceipt(TextWriter output, Shipment shipment)
    {
        output.WriteLine("RECEIPT");
        WriteSummary(output, shipment);
    }

    public static void PrintDelayNotice(TextWriter output, Shipment shipment)
    {
        output.WriteLine("DELAY NOTICE");
        WriteSummary(output, shipment);
    }

    private static void WriteSummary(TextWriter output, Shipment shipment)
    {
        output.WriteLine($"Tracking: {shipment.TrackingCode}");
        output.WriteLine($"Carrier: {shipment.Carrier}");
        output.WriteLine($"ETA: {shipment.Eta:d}");
    }
}
```

Step 2: extract what stays (temporary name `ZzTmp`), then inline `WriteSummary` into each caller and delete it. Step 6: rename `ZzTmp` back to `WriteSummary`.

After: the arrival line now lives in the callers, and the delay notice can change it.

```csharp
using System;
using System.IO;

public static class ShipmentPrinter
{
    public static void PrintReceipt(TextWriter output, Shipment shipment)
    {
        output.WriteLine("RECEIPT");
        WriteSummary(output, shipment);
        output.WriteLine($"ETA: {shipment.Eta:d}");
    }

    public static void PrintDelayNotice(TextWriter output, Shipment shipment)
    {
        output.WriteLine("DELAY NOTICE");
        WriteSummary(output, shipment);
        output.WriteLine($"ETA: {shipment.Eta:d}");
    }

    private static void WriteSummary(TextWriter output, Shipment shipment)
    {
        output.WriteLine($"Tracking: {shipment.TrackingCode}");
        output.WriteLine($"Carrier: {shipment.Carrier}");
    }
}
```

Behavior is unchanged at this point. The next change (a revised arrival window in the delay notice) now touches only `PrintDelayNotice`.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
