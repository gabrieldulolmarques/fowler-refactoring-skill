# Inline Class

Fowler (2018), ch. 7, p. 186. Formerly / aka: —. Inverse: Extract Class
([extract-class.md](extract-class.md)).

## When to use
Smells: Lazy Element, Speculative Generality, Shotgun Surgery.

- A class has so little left (often after other refactorings moved its members out) that it
  adds a name and an indirection but no meaning. Fold it into the class that uses it most.
- Two classes split their responsibilities badly. It can be easier to merge them first and
  then apply Extract Class ([extract-class.md](extract-class.md)) along the right line than to shuffle
  members one by one.
- Do not use it when the class has several unrelated clients that would each need the same
  members copied or re-exposed, or when it carries a real responsibility that just happens to
  be small.

## Mechanics
1. Pick the target: the class that uses the source class most.
2. In the target, add a delegating member for every public member of the source that clients
   use. Each one just forwards to the source object.
3. Compile and test.
4. Redirect clients one at a time so they call the target's delegators instead of reaching
   through to the source. Compile and test after each change.
5. Inline any source method that only makes sense as a whole (see [inline-function.md](../first-set/inline-function.md))
   so its body lives in the target.
6. Move the source's fields and methods into the target one at a time, replacing each
   delegator with the real member. Compile and test after each move.
7. Move any construction or initialization of the source's data into the target's
   constructor.
8. When the source class is empty and nothing references it, delete it. Compile and test.

## Example
Before: `TrialTerms` holds little and is only used by `Subscription`.

```csharp
using System;

public class TrialTerms
{
    public int Days { get; set; }
    public string Label { get; set; } = "";

    public string Describe() => $"{Label} ({Days} days)";
}

public class Subscription
{
    public Subscription(DateTime startedOn) => StartedOn = startedOn;

    public TrialTerms Trial { get; } = new TrialTerms();
    public DateTime StartedOn { get; }

    public DateTime TrialEnd => StartedOn.AddDays(Trial.Days);
    public string TrialSummary => Trial.Describe();
}

public static class Client
{
    public static void Configure(Subscription subscription)
    {
        subscription.Trial.Days = 14;
        subscription.Trial.Label = "Standard";
    }
}
```

Step 2 and 4: add delegators to `Subscription`, then change clients to use them.

```csharp
using System;

public class Subscription
{
    public Subscription(DateTime startedOn) => StartedOn = startedOn;

    public TrialTerms Trial { get; } = new TrialTerms();
    public DateTime StartedOn { get; }

    public int TrialDays
    {
        get => Trial.Days;
        set => Trial.Days = value;
    }

    public string TrialLabel
    {
        get => Trial.Label;
        set => Trial.Label = value;
    }

    public DateTime TrialEnd => StartedOn.AddDays(Trial.Days);
    public string TrialSummary => Trial.Describe();
}

public static class Client
{
    public static void Configure(Subscription subscription)
    {
        subscription.TrialDays = 14;
        subscription.TrialLabel = "Standard";
    }
}
```

Steps 5 to 8: move the data and the behavior, then delete `TrialTerms`.

```csharp
using System;

public class Subscription
{
    public Subscription(DateTime startedOn) => StartedOn = startedOn;

    public DateTime StartedOn { get; }
    public int TrialDays { get; set; }
    public string TrialLabel { get; set; } = "";

    public DateTime TrialEnd => StartedOn.AddDays(TrialDays);
    public string TrialSummary => $"{TrialLabel} ({TrialDays} days)";
}

public static class Client
{
    public static void Configure(Subscription subscription)
    {
        subscription.TrialDays = 14;
        subscription.TrialLabel = "Standard";
    }
}
```

Behavior is unchanged. Only the client code that reached through `Trial` changed shape, and
that happened before the class disappeared.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
