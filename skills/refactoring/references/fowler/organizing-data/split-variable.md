# Split Variable

Fowler (2018), ch. 9, p. 240. Formerly / aka: formerly Remove Assignments to Parameters, formerly Split Temp. Inverse: —.

## When to use
Smell: Mutable Data.

A variable that holds the result of some computation for later reference should be assigned once. If it is assigned a second time with a value that means something else, it has two jobs, and the reader must track which one it has at each line. Give each job its own variable and its own name.

Leave alone:
- Loop variables, which change on every iteration by design.
- Collecting variables, which accumulate a value (`total = total + x`, string building, adding to a collection). Their later assignments depend on the earlier value, so they are one responsibility.

Assigning to an input parameter is a common case: the parameter is both the input and the working result. Splitting it separates "what the caller gave me" from "what I am computing".

## Mechanics
1. Pick the first value the variable holds. At its declaration and first assignment, rename the variable to a name that describes only that first use.
2. Update every reference that reads this first value, stopping before the second assignment.
3. Compile and test.
4. At the second assignment, declare a new variable and name it for that second use. If the language allows, declare it immutable (C# has no immutable locals; see the C# notes).
5. Repeat steps 2 to 4 for each later assignment, testing after each stage. At the final assignment the original name has no references left.
6. For a parameter: declare a local initialized from the parameter at the top of the function, rename the parameter to say it is the original input, and point the reads that mean the original input at the parameter. Then continue with the steps above on the local, renaming it to say what it holds.

## Example
Before: `value` first holds the uncalibrated temperature and is then reused for the calibrated one, which is a different quantity.

```csharp
using System;

public class Sample
{
    public int RawCounts { get; set; }
    public double CountsToCelsius { get; set; }
    public double SelfHeating { get; set; }
}

public class Calibration
{
    public double Offset { get; set; }
    public double Gain { get; set; }
}

public class Report
{
    public double ReportedTemperature(Sample sample, Calibration calibration)
    {
        double value = sample.RawCounts * sample.CountsToCelsius;
        Console.WriteLine($"Uncalibrated: {value}");

        value = (value - calibration.Offset) * calibration.Gain;
        return value - sample.SelfHeating;
    }
}
```

After: one variable per responsibility, each named for what it holds.

```csharp
public class Report
{
    public double ReportedTemperature(Sample sample, Calibration calibration)
    {
        double uncalibrated = sample.RawCounts * sample.CountsToCelsius;
        Console.WriteLine($"Uncalibrated: {uncalibrated}");

        double calibrated = (uncalibrated - calibration.Offset) * calibration.Gain;
        return calibrated - sample.SelfHeating;
    }
}
```

Parameter case. Before, `requested` is both the input and the effective sampling interval:

```csharp
public class Scheduler
{
    public double EffectiveInterval(double requested, bool lowBattery)
    {
        requested = Math.Max(requested, 0.5) + 0.25;
        if (lowBattery) requested *= 4;
        return requested;
    }
}
```

Intermediate: the parameter is renamed to say it is the input, and a local takes over as the working value.

```csharp
public class Scheduler
{
    public double EffectiveInterval(double requestedSeconds, bool lowBattery)
    {
        double requested = requestedSeconds;
        requested = Math.Max(requested, 0.5) + 0.25;
        if (lowBattery) requested *= 4;
        return requested;
    }
}
```

After: the local is renamed for what it holds.

```csharp
public class Scheduler
{
    public double EffectiveInterval(double requestedSeconds, bool lowBattery)
    {
        double interval = Math.Max(requestedSeconds, 0.5) + 0.25;
        if (lowBattery) interval *= 4;
        return interval;
    }
}
```

## C# notes
- C# has no immutable local variables (`const` only fits compile-time constants), so keep each new variable assigned exactly once.
- Renaming a parameter on a public method breaks callers that pass it by name (named arguments).

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- No variable is assigned twice for different purposes; the only repeated assignments left are loop counters and collecting variables.
