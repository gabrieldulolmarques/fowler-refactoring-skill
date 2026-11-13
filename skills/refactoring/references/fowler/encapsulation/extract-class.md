# Extract Class

Fowler (2018), ch. 7, p. 182. Formerly / aka: —. Inverse: Inline Class
([inline-class.md](inline-class.md)).

## When to use
Smells: Large Class, Divergent Change, Data Clumps, Primitive Obsession, Temporary Field.

- A class has grown into many fields and methods, and part of it can be understood on its own.
- A subset of the fields and methods belongs together: the fields change together or depend on each other.
- Test: remove one field or method in your head. If other members become meaningless, they belong in the same extracted class.
- Subtyping or variation affects only some of the class's features, or different features vary in different ways.

Do not use it when the pieces are tightly entangled with the rest and there is no clear
responsibility to name. Also skip it for a class that is small and cohesive.

## Mechanics
1. Decide which responsibility to split off and name it.
2. Create the new, empty class. If the original's name no longer describes what is left, rename it.
3. Give the original an instance of the new class, created in its constructor, and keep it in a private field.
4. Move the fields one at a time ([move-field.md](../moving-features/move-field.md)). The original's members now delegate to the new class. Compile and test after each field.
5. Move the methods one at a time ([move-function.md](../moving-features/move-function.md)), starting with the lowest-level ones (those that are called rather than those that call). Compile and test after each method.
6. Review both public interfaces: remove methods that are no longer needed and rename members to fit their new context (the new class does not need the old prefixes or qualifiers).
7. Decide whether to expose the new object to clients. If so, consider making it a value object ([change-reference-to-value.md](../organizing-data/change-reference-to-value.md)) first.

## Example
Before: a subscription class that also holds the usage allowance data and its overage rule.

```csharp
using System;

public class Subscription
{
    private string _planName;
    private int _includedUnits;
    private int _usedUnits;
    private decimal _overageRate;

    public Subscription(string planName, int includedUnits, int usedUnits, decimal overageRate)
    {
        _planName = planName;
        _includedUnits = includedUnits;
        _usedUnits = usedUnits;
        _overageRate = overageRate;
    }

    public string PlanName => _planName;
    public int IncludedUnits => _includedUnits;
    public int UsedUnits => _usedUnits;
    public decimal OverageRate => _overageRate;

    public int OverageUnits => Math.Max(0, _usedUnits - _includedUnits);
    public decimal OverageCharge => OverageUnits * _overageRate;
}
```

After: the allowance data and behavior live in `UsageAllowance`; `Subscription` keeps its public
members as delegates, so callers do not change.

```csharp
using System;

public class UsageAllowance
{
    public UsageAllowance(int includedUnits, int usedUnits, decimal overageRate)
    {
        IncludedUnits = includedUnits;
        UsedUnits = usedUnits;
        OverageRate = overageRate;
    }

    public int IncludedUnits { get; }
    public int UsedUnits { get; }
    public decimal OverageRate { get; }

    public int OverageUnits => Math.Max(0, UsedUnits - IncludedUnits);
    public decimal OverageCharge => OverageUnits * OverageRate;
}

public class Subscription
{
    private readonly string _planName;
    private readonly UsageAllowance _allowance;

    public Subscription(string planName, int includedUnits, int usedUnits, decimal overageRate)
    {
        _planName = planName;
        _allowance = new UsageAllowance(includedUnits, usedUnits, overageRate);
    }

    public string PlanName => _planName;
    public int IncludedUnits => _allowance.IncludedUnits;
    public int UsedUnits => _allowance.UsedUnits;
    public decimal OverageRate => _allowance.OverageRate;

    public int OverageUnits => _allowance.OverageUnits;
    public decimal OverageCharge => _allowance.OverageCharge;
}
```

A later step can expose `UsageAllowance` to clients and drop the delegates.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Behavior is unchanged: the original class's public members return the same values as before.
