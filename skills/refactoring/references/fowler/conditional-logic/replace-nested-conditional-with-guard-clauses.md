# Replace Nested Conditional with Guard Clauses

Fowler (2018), ch. 10, p. 266. Formerly / aka: —. Inverse: —.

## When to use
- A conditional has one leg that is the normal behavior and other legs that are unusual
  or terminal cases (invalid input, missing data, "nothing to do").
- Nesting pushes the real work to the right, and the reader must keep every enclosing
  condition in mind to understand it.
- A `result` variable is assigned in several branches only to be returned at the end.

A guard clause marks a case as a side path: dispatch it and exit. An if/else presents two
paths as equally ordinary. Choose the shape that matches what the code means.

Do not use it when both legs are normal behavior: keep a plain if/else. Single-exit is a
style preference, so decide by readability.

## Mechanics
1. Pick the outermost condition that guards an unusual case and rewrite it as a guard
   clause: test the unusual case, return its result right away. If the condition guards
   the normal case instead, invert it first (apply De Morgan if needed, and simplify any
   leftover `!`) so that the unusual case becomes the early return.
2. Compile and run the tests.
3. Repeat for the next condition, working inward, one guard at a time.
4. When the guards no longer need the result variable, remove it and return values
   directly.
5. If several guards return the same value, merge them with
   Consolidate Conditional Expression ([consolidate-conditional-expression.md](consolidate-conditional-expression.md)).

## Example
Before: the fee is only computed when the order is neither cancelled nor empty.

```csharp
public decimal ShippingFee(Order order)
{
    decimal result;
    if (order.IsCancelled)
    {
        result = 0m;
    }
    else
    {
        if (order.Items.Count == 0)
        {
            result = 0m;
        }
        else
        {
            if (order.Total >= 100m)
            {
                result = 0m;
            }
            else
            {
                result = 7.5m + order.Items.Count * 0.5m;
            }
        }
    }
    return result;
}
```

After the first guard (one step, tests run):

```csharp
public decimal ShippingFee(Order order)
{
    decimal result;
    if (order.IsCancelled) return 0m;
    if (order.Items.Count == 0)
    {
        result = 0m;
    }
    else
    {
        if (order.Total >= 100m) result = 0m;
        else result = 7.5m + order.Items.Count * 0.5m;
    }
    return result;
}
```

Final, with the variable gone and the equal results consolidated:

```csharp
public decimal ShippingFee(Order order)
{
    if (order.IsCancelled || order.Items.Count == 0 || order.Total >= 100m) return 0m;
    return 7.5m + order.Items.Count * 0.5m;
}
```

Reversing a condition: when an `||` test guards the normal path, invert it (De Morgan
turns the `||` into `&&`).

```csharp
// before
public decimal AmountDue(Invoice invoice)
{
    if (invoice.IsOpen || invoice.IsOverdue)
    {
        if (invoice.Customer != null)
            return invoice.Amount - invoice.Paid;
    }
    return 0m;
}

// after
public decimal AmountDue(Invoice invoice)
{
    if (!invoice.IsOpen && !invoice.IsOverdue) return 0m;
    if (invoice.Customer == null) return 0m;
    return invoice.Amount - invoice.Paid;
}
```

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Each guard keeps the original return value for its case, and the order of the guards
  matches the original order of evaluation (a guard that calls something with side effects
  must not move before another).
