# Replace Primitive with Object

Fowler (2018), ch. 7, p. 174. Formerly / aka: Replace Data Value with Object, Replace Type Code with Class. Inverse: —.

## When to use
Smell: Primitive Obsession. A plain `string` or `int` stands for a domain concept, and logic about it (validation, formatting, comparison, extracting parts) is starting to appear, or is duplicated across the code base. Wrapping the value gives that logic one home.

Do it as soon as you want to do more with the value than print or store it. The first version of the type can be a bare wrapper, since it gives later behavior a place to land. This is a judgment call: if the value is only passed through and never inspected, a wrapper may not be worth it.

## Mechanics
1. If the value is a bare field, apply Encapsulate Variable first ([encapsulate-variable.md](../first-set/encapsulate-variable.md)), so all reads and writes go through one getter and setter.
2. Create a small value type that takes the existing primitive in its constructor and exposes it (in C#, `ToString()` or an explicit conversion usually reads better than a generic `Value` property).
3. Build and run static checks.
4. Change the setter to construct the new type and store that, changing the field's type.
5. Change the getter to return the primitive obtained from the new type, so callers still see the old type.
6. Build and test.
7. Rename the original accessors ([change-function-declaration.md](../first-set/change-function-declaration.md)) if they now mislead, for example a getter that returns a description string rather than the concept.
8. Decide whether it is a value object or a reference object ([change-reference-to-value.md](../organizing-data/change-reference-to-value.md), [change-value-to-reference.md](../organizing-data/change-value-to-reference.md)).

Next, optionally: add an accessor that returns the new object and migrate callers to it one at a time, then move validation, comparison and formatting onto the type, making it immutable with value equality. Each of those is its own small, tested change.

## Example
Before: a subscription's coupon is a string, and callers pick it apart.

```csharp
using System.Collections.Generic;
using System.Linq;

public class Subscription
{
    public string Coupon { get; set; } = "";
}

public static class Reports
{
    public static int CountByCampaign(IEnumerable<Subscription> subscriptions, string campaign) =>
        subscriptions.Count(s => s.Coupon.StartsWith(campaign + "-"));
}
```

After: a value type owns validation and the campaign.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

public sealed class CouponCode
{
    private readonly string _value;

    public CouponCode(string value)
    {
        var parts = (value ?? "").Split('-');
        if (parts.Length != 2 || parts[0].Length == 0
            || !int.TryParse(parts[1], out var percent) || percent < 1 || percent > 100)
            throw new ArgumentException($"'{value}' is not a coupon code like SPRING-15");
        _value = value!;
        Campaign = parts[0];
        PercentOff = percent;
    }

    public string Campaign { get; }
    public int PercentOff { get; }
    public override string ToString() => _value;
}

public class Subscription
{
    private CouponCode _coupon;

    public Subscription(string coupon) => _coupon = new CouponCode(coupon);

    public CouponCode Coupon => _coupon;

    // Old accessor kept for existing callers, renamed because it now returns text.
    public string CouponText
    {
        get => _coupon.ToString();
        set => _coupon = new CouponCode(value);
    }
}

public static class Reports
{
    public static int CountByCampaign(IEnumerable<Subscription> subscriptions, string campaign) =>
        subscriptions.Count(s => s.Coupon.Campaign == campaign);
}
```

Same behavior for valid codes; a malformed code is now rejected when it is assigned, not discovered later. The subscription is always built with a coupon, so `Coupon` is never null.

## C# notes
- A meaningful `string` or `int` becomes its own type: a `record`, or a `readonly record struct` for small values (C# 9+ for `record`, C# 10 for `readonly record struct`; on Unity it needs an `IsExternalInit` shim). If the legal values are a fixed closed set with no extra behavior, an `enum` may be enough.
- A `record` gives value equality for free; keep the state immutable.
- A `readonly record struct` can be `default`, which skips the constructor and its validation. A `with` expression on a record also copies state without running validation. Use a `sealed class` when either matters.
- An `enum` is weaker than a wrapper: any integer can be cast to it without a check.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Grep for the old primitive's raw comparisons and parsing (string literals, `StartsWith`, `Substring`); none should remain outside the new type.
- Every construction site goes through the validating constructor.
