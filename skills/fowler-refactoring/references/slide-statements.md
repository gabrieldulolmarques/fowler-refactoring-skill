# Slide Statements

Fowler (2018), ch. 8, p. 223. Formerly / aka: formerly Consolidate Duplicate Conditional Fragments. Inverse: none listed.

## When to use
Smells: Duplicated Code, Mutable Data (and as a step inside Long Function).
- Lines that touch the same data are separated by lines that touch something else.
- A variable is declared far above its first use (declare it just before it is needed).
- You want to extract a group of lines but they are interleaved with other code. Sliding them together first makes the extraction possible.
- The same statements appear at the start or end of every branch of a conditional.

Not worth it if the slide cannot be made safe in small steps: do other preparation first (for example Split Variable on a reused variable) and come back.

## Mechanics
1. Choose the target position for the fragment (the statement or block you will move).
2. Check every statement between the fragment and the target for interference. Give up on this slide if any of these holds:
   - Moving up: the fragment would pass the declaration or assignment of something it reads.
   - Moving down: the fragment would pass a statement that reads something the fragment defines or changes.
   - The fragment would pass a statement that modifies something the fragment reads or writes.
   - The fragment modifies something that a statement in between reads.
   Statements without side effects can be reordered freely. Be careful with calls: only treat a call as side-effect free if you know it is.
3. Cut the fragment and paste it at the target.
4. Compile and run the tests.
5. If a test fails, undo and retry with a smaller step: slide over fewer statements, or move a smaller fragment. If that still fails, the slide may not be worth it yet.

Sliding out of a conditional: when the same statements end (or begin) every branch, and they do not depend on which branch ran in a way that changes behavior, remove them from each branch and put one copy after (or before) the conditional. Sliding into a conditional is the reverse and repeats the fragment in every branch.

## Example
Before: the discount lines are mixed with the shipping lines, and `shippingCost` is declared early.

```csharp
public decimal Total(Invoice invoice)
{
    decimal shippingCost;
    var customer = invoice.Customer;
    decimal discount = 0m;
    var subtotal = invoice.Lines.Sum(l => l.Quantity * l.UnitPrice);
    shippingCost = invoice.Weight * 0.5m;
    if (customer.IsPremium) discount = subtotal * 0.1m;
    if (subtotal > 500m) shippingCost = 0m;
    return subtotal - discount + shippingCost;
}
```

After: each declaration sits next to its use, and the discount lines are adjacent, ready for Extract Function.

```csharp
public decimal Total(Invoice invoice)
{
    var subtotal = invoice.Lines.Sum(l => l.Quantity * l.UnitPrice);

    var customer = invoice.Customer;
    decimal discount = 0m;
    if (customer.IsPremium) discount = subtotal * 0.1m;

    decimal shippingCost = invoice.Weight * 0.5m;
    if (subtotal > 500m) shippingCost = 0m;

    return subtotal - discount + shippingCost;
}
```

Why it was safe: `subtotal` is declared before everything that reads it, and the shipping lines read and write only `shippingCost`, `invoice` and `subtotal`, none of which the discount lines change.

Conditional case, before and after (same behavior):

```csharp
// before
if (account.Balance >= amount)
{
    account.Debit(amount);
    auditLog.Add(account.Id);
}
else
{
    account.Overdraft(amount);
    auditLog.Add(account.Id);
}

// after
if (account.Balance >= amount)
    account.Debit(amount);
else
    account.Overdraft(amount);
auditLog.Add(account.Id);
```

This is only valid because the branches do not change what `auditLog.Add(account.Id)` observes.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- If coverage of the moved code is weak, add tests first: a slide that passes through shared mutable state is the kind of change tests catch best.
