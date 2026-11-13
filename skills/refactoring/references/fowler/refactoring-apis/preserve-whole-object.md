# Preserve Whole Object

Fowler (2018), ch. 11, p. 319. Formerly / aka: —. Inverse: —.

## When to use
Smells: Long Function, Long Parameter List, Data Clumps.

- Callers read two or more values from one object and pass them on. Pass the object instead.
- The signature stops changing when the function later needs another field of that object.
- Several callers repeat the same logic over the unpacked parts. That logic often belongs on the whole object (Feature Envy; see [move-function.md](../moving-features/move-function.md)).
- Common right after Introduce Parameter Object ([introduce-parameter-object.md](../first-set/introduce-parameter-object.md)): hunt down the remaining call sites that still unpack the data.
- If several callers only ever use the same subset of the object's members, consider [extract-class.md](../encapsulation/extract-class.md).
- An object calling another object with several of its own values can pass `this` instead.

Do not use it when the callee must not depend on the whole object's type, typically because they live in different modules or layers. Then keep the primitive parameters, or pass a smaller object.

## Mechanics
1. Declare a new, empty method with the signature you want (the whole object as parameter). Give it a unique, easy-to-search temporary name.
2. Make its body call the old method, mapping from the whole object to the old parameters.
3. Compile (static checks).
4. Change callers one at a time to use the new method, compiling and testing after each. Locals that only fed the old arguments may become dead; remove them ([remove-dead-code.md](../moving-features/remove-dead-code.md)).
5. When no caller of the old method is left, inline the old method into the new one ([inline-function.md](../first-set/inline-function.md)).
6. Rename the new method to the original name, and update its callers (the unique temporary name lets a plain text search find every call site to update).

Variation: if you prefer to build the new method from other refactorings, use [extract-variable.md](../first-set/extract-variable.md) on the call and on the object expression at one caller, then [extract-function.md](../first-set/extract-function.md) on the call, and [move-function.md](../moving-features/move-function.md) if it belongs on the callee's class. Continue from step 4.

## Example
Before:

```csharp
using System;
using System.Collections.Generic;

public class TimeWindow
{
    public TimeWindow(TimeSpan start, TimeSpan end)
    {
        Start = start;
        End = end;
    }

    public TimeSpan Start { get; }
    public TimeSpan End { get; }
}

public class ScheduledNotification
{
    public ScheduledNotification(TimeWindow window)
    {
        Window = window;
    }

    public TimeWindow Window { get; }
}

public class QuietHoursPolicy
{
    private readonly TimeWindow _allowed = new(TimeSpan.FromHours(8), TimeSpan.FromHours(21));

    public bool Allows(TimeSpan start, TimeSpan end) =>
        start >= _allowed.Start && end <= _allowed.End;
}

public class NotificationAuditor
{
    public void Audit(ScheduledNotification notification, QuietHoursPolicy policy, List<string> findings)
    {
        var from = notification.Window.Start;
        var to = notification.Window.End;
        if (!policy.Allows(from, to))
            findings.Add("delivery window falls inside quiet hours");
    }
}
```

Intermediate (steps 1 to 2; the new method delegates to the old one):

```csharp
// fragment
public bool xxNewAllows(TimeWindow window) => Allows(window.Start, window.End);
```

After (callers migrated, old method inlined, temporary name removed):

```csharp
public class QuietHoursPolicy
{
    private readonly TimeWindow _allowed = new(TimeSpan.FromHours(8), TimeSpan.FromHours(21));

    public bool Allows(TimeWindow window) =>
        window.Start >= _allowed.Start && window.End <= _allowed.End;
}

public class NotificationAuditor
{
    public void Audit(ScheduledNotification notification, QuietHoursPolicy policy, List<string> findings)
    {
        if (!policy.Allows(notification.Window))
            findings.Add("delivery window falls inside quiet hours");
    }
}
```

Behavior is the same; the `from` and `to` locals are gone.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- After step 5, a search for the old method's name finds no remaining caller. After step 6, a search for the temporary prefix (`xx`) finds nothing.
