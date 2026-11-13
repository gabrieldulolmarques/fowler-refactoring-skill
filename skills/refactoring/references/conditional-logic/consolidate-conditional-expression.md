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
public decimal RefundAmount(Order order)
{
    if (order.IsDigital) return 0m;
    if (order.DaysSinceDelivery > 30) return 0m;
    if (order.IsFinalSale) return 0m;

    return order.Total - order.RestockingFee;
}
```

After merging, then extracting:

```csharp
public decimal RefundAmount(Order order)
{
    if (IsNotRefundable(order)) return 0m;

    return order.Total - order.RestockingFee;
}

private static bool IsNotRefundable(Order order) =>
    order.IsDigital
    || order.DaysSinceDelivery > 30
    || order.IsFinalSale;
```

Nested form, merged with `&&`:

```csharp
// before
if (customer.IsActive)
    if (customer.Balance > 0m)
        SendReminder(customer);

// after
if (customer.IsActive && customer.Balance > 0m)
    SendReminder(customer);
```

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
