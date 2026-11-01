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
2. C# has no immutable local variables (`const` only fits compile-time constants), so just keep the new variable assigned exactly once.
3. Update every reference that reads this first value, stopping before the second assignment.
4. Compile and test.
5. At the second assignment, declare a new variable and name it for that second use.
6. Repeat steps 3 to 5 for each later assignment, testing after each stage. At the final assignment the original name has no references left.
7. For a parameter: declare a local initialized from the parameter at the top of the function, rename the parameter to say it is the original input, and point the reads that mean the original input at the parameter. Then continue with the steps above on the local, renaming it to say what it holds.

## Example
Before: `amount` first holds the order subtotal and is then reused for the amount after the discount, which is a different quantity.

```csharp
public decimal InvoiceTotal(Order order, Customer customer)
{
    decimal amount = order.Quantity * order.UnitPrice;
    Console.WriteLine($"Subtotal: {amount}");

    amount = amount - amount * customer.DiscountRate;
    return amount + order.ShippingFee;
}
```

After: one variable per responsibility, each named for what it holds.

```csharp
public decimal InvoiceTotal(Order order, Customer customer)
{
    decimal subtotal = order.Quantity * order.UnitPrice;
    Console.WriteLine($"Subtotal: {subtotal}");

    decimal discounted = subtotal - subtotal * customer.DiscountRate;
    return discounted + order.ShippingFee;
}
```

Parameter case. Before, `weight` is both the input and the shipping cost:

```csharp
public decimal ShippingCost(decimal weight, bool express)
{
    weight = Math.Max(weight, 1m) * 4.5m;
    if (express) weight *= 1.8m;
    return weight;
}
```

Intermediate: the parameter is renamed to say it is the input, and a local takes over as the working value.

```csharp
public decimal ShippingCost(decimal weightKg, bool express)
{
    decimal weight = weightKg;
    weight = Math.Max(weight, 1m) * 4.5m;
    if (express) weight *= 1.8m;
    return weight;
}
```

After: the local is renamed for what it holds.

```csharp
public decimal ShippingCost(decimal weightKg, bool express)
{
    decimal cost = Math.Max(weightKg, 1m) * 4.5m;
    if (express) cost *= 1.8m;
    return cost;
}
```

## C# notes
Renaming a parameter on a public method breaks callers that pass it by name (named arguments).

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- No variable is assigned twice for different purposes; the only repeated assignments left are loop counters and collecting variables.
