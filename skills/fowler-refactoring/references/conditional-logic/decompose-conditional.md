# Decompose Conditional

Fowler (2018), ch. 10, p. 260. Formerly / aka: —. Inverse: —. It is Extract Function
([extract-function.md](../first-set/extract-function.md)) applied to the parts of a conditional.

## When to use
Smells: Long Function (conditional logic that hides the intent).

- The condition is a compound boolean expression and the reader must work out what it means.
- The branches hold calculations or sequences of statements whose purpose is not obvious.
- A comment above the `if` explains the condition, or comments label each branch.

Naming is the point: the condition gets a name for the business question it asks, and each
branch gets a name for what it produces. Skip it when the condition and branches are already
one-liners that read like the intent.

## Mechanics
1. Extract the condition into its own function (or property) named for the question it asks.
   Compile and test.
2. Extract the body of the `then` branch into a function named for its result. Compile and
   test.
3. Extract the body of the `else` branch the same way. Compile and test.
4. For an `else if` chain, treat each further condition and branch the same way, one at a time.
5. Optionally, when each branch only assigns or returns a value, rewrite the statement as a
   ternary expression (`x = Condition() ? A() : B();`). Compile and test.

## Example
Before:

```csharp
public decimal ShippingCost(Order order, DateTime today)
{
    decimal cost;
    if (today >= order.Promo.Start && today <= order.Promo.End && order.Total >= order.Promo.MinimumTotal)
        cost = order.Weight * order.Promo.RatePerKg;
    else
        cost = order.Weight * order.StandardRatePerKg + order.HandlingFee;
    return cost;
}
```

After:

```csharp
public decimal ShippingCost(Order order, DateTime today)
{
    return QualifiesForPromo(order, today)
        ? PromoShipping(order)
        : StandardShipping(order);
}

private static bool QualifiesForPromo(Order order, DateTime today) =>
    today >= order.Promo.Start
    && today <= order.Promo.End
    && order.Total >= order.Promo.MinimumTotal;

private static decimal PromoShipping(Order order) =>
    order.Weight * order.Promo.RatePerKg;

private static decimal StandardShipping(Order order) =>
    order.Weight * order.StandardRatePerKg + order.HandlingFee;
```

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
