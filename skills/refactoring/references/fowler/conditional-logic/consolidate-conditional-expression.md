# Consolidate Conditional Expression

Fowler (2018), ch. 10, p. 263. Formerly / aka: —. Inverse: —.

## When to use
- Several `if` statements in a row, each with a different test but the same outcome (same return value, same action).
- Nested `if` statements with no `else`, where only the innermost one does something.
- You want to name the combined rule ("is eligible", "is blocked") by extracting it afterwards ([extract-function.md](../first-set/extract-function.md)).

Do not use it when the checks are independent concerns that only happen to share a result today. Merging them hides that each one can change on its own. Decompose instead, or leave them separate.

## Mechanics
1. Check that none of the conditions has side effects (no writes, no calls that change state or consume input). If one does, first separate the query from the modifier ([separate-query-from-modifier.md](../refactoring-apis/separate-query-from-modifier.md)).
2. Pick two adjacent checks that share the outcome and merge their conditions into one `if`. Consecutive checks join with `||`; nested checks join with `&&`.
3. Compile and run the tests.
4. Repeat with the next check until a single condition remains.
5. Consider extracting the combined condition into a function with an intention-revealing name ([extract-function.md](../first-set/extract-function.md)).

Order matters when conditions can throw or are costly: `||` and `&&` short-circuit like the original sequence did, so keep the original left-to-right order.

## Example
Before:

```csharp
using System;

public class Cart
{
    public decimal Subtotal { get; }
    public bool ContainsGiftCard { get; }

    public Cart(decimal subtotal, bool containsGiftCard)
    {
        Subtotal = subtotal;
        ContainsGiftCard = containsGiftCard;
    }
}

public class Coupon
{
    public DateTime ExpiresOn { get; }
    public decimal MinimumSubtotal { get; }
    public decimal Percentage { get; }
    public bool IsSingleUse { get; }

    public Coupon(DateTime expiresOn, decimal minimumSubtotal, decimal percentage, bool isSingleUse)
    {
        ExpiresOn = expiresOn;
        MinimumSubtotal = minimumSubtotal;
        Percentage = percentage;
        IsSingleUse = isSingleUse;
    }
}

public class CouponService
{
    public decimal Discount(Cart cart, Coupon coupon, DateTime today)
    {
        if (today > coupon.ExpiresOn) return 0m;
        if (cart.Subtotal < coupon.MinimumSubtotal) return 0m;
        if (cart.ContainsGiftCard) return 0m;

        return cart.Subtotal * coupon.Percentage;
    }
}
```

After merging, then extracting:

```csharp
public class CouponService
{
    public decimal Discount(Cart cart, Coupon coupon, DateTime today)
    {
        if (IsNotApplicable(cart, coupon, today)) return 0m;

        return cart.Subtotal * coupon.Percentage;
    }

    private static bool IsNotApplicable(Cart cart, Coupon coupon, DateTime today) =>
        today > coupon.ExpiresOn
        || cart.Subtotal < coupon.MinimumSubtotal
        || cart.ContainsGiftCard;
}
```

Nested form, merged with `&&`:

```csharp
public class CouponBadge
{
    public void ShowBefore(Cart cart, Coupon coupon)
    {
        if (coupon.IsSingleUse)
            if (cart.Subtotal >= coupon.MinimumSubtotal)
                ShowBadge(cart);
    }

    public void ShowAfter(Cart cart, Coupon coupon)
    {
        if (coupon.IsSingleUse && cart.Subtotal >= coupon.MinimumSubtotal)
            ShowBadge(cart);
    }

    private void ShowBadge(Cart cart) { }
}
```

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
