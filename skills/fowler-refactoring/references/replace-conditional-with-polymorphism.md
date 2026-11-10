# Replace Conditional with Polymorphism

Fowler (2018), ch. 10, p. 272. Formerly / aka: —. Inverse: —.

## When to use
Smells: Repeated Switches, Primitive Obsession, Long Function.

- Several functions switch on the same type code (account kind, document type, plan). Each new kind forces you to edit every switch. Moving each kind into a class puts all of its behavior in one place and removes the duplication.
- One case is the normal path and a few others tweak it. Keep the normal path in the base class and give each tweak its own subclass.

A plain `if`/`switch` is usually enough. Use this when the same conditional is repeated or hard to follow and the cases are real kinds.

## Mechanics
1. Optional first step: if the logic is spread over free functions, group them first with [combine-functions-into-class.md](combine-functions-into-class.md).
2. If no classes exist for the cases, create them: a base class (or interface) with one subclass per case, plus a factory function that returns the right instance.
3. Change callers to get the object from the factory instead of constructing it or passing the type code around. Compile and test.
4. If the conditional is not already a self-contained method, isolate it with [extract-function.md](extract-function.md), then place that method on the base class.
5. Pick one case. Add an override in its subclass containing that branch's logic, adjusted to use the subclass's own members. Optionally make the matching branch in the base method throw, so a test fails if it is still reached. Compile and test.
6. Repeat step 5 for every branch, testing after each.
7. Decide what the base method does. Keep the default branch as the base implementation, or, if the base class should never be used alone, make the method `abstract`. If the base stays concrete, the factory must return the base class for unknown values; if it is abstract, the factory must reject them.
8. Remove the now-empty `switch` and, if nothing else uses it, the type code. Keep the code as a property until its last reader is gone.
9. For a base-and-variant case, you may need to extract the varying part of a large method first, so the subclass can override only that part and call `base` for the rest. Name the extracted pieces after what they mean, not after the case.

## Example
Before: two methods switch on the same account kind.

```csharp
using System;

public enum AccountKind { Standard, Premium, Student }

public class Account
{
    public AccountKind Kind { get; }
    public decimal Balance { get; }

    public Account(AccountKind kind, decimal balance)
    {
        Kind = kind;
        Balance = balance;
    }

    public decimal MonthlyFee()
    {
        switch (Kind)
        {
            case AccountKind.Standard: return 5m;
            case AccountKind.Premium: return Balance > 10000m ? 0m : 12m;
            case AccountKind.Student: return 0m;
            default: throw new InvalidOperationException();
        }
    }

    public int FreeTransfers()
    {
        switch (Kind)
        {
            case AccountKind.Standard: return 3;
            case AccountKind.Premium: return 20;
            case AccountKind.Student: return 5;
            default: throw new InvalidOperationException();
        }
    }
}
```

After: one class per kind, created by a factory; the switches are gone. An unknown kind now fails when the object is created instead of when a method is called (same exception type). In this example nothing reads `Kind` any more, so it was removed. In real code keep it until its last reader is gone.

```csharp
using System;

public enum AccountKind { Standard, Premium, Student }

public abstract class Account
{
    public decimal Balance { get; }

    protected Account(decimal balance) => Balance = balance;

    public static Account Create(AccountKind kind, decimal balance) => kind switch
    {
        AccountKind.Standard => new StandardAccount(balance),
        AccountKind.Premium => new PremiumAccount(balance),
        AccountKind.Student => new StudentAccount(balance),
        _ => throw new InvalidOperationException()
    };

    public abstract decimal MonthlyFee();
    public abstract int FreeTransfers();
}

public class StandardAccount : Account
{
    public StandardAccount(decimal balance) : base(balance) { }
    public override decimal MonthlyFee() => 5m;
    public override int FreeTransfers() => 3;
}

public class PremiumAccount : Account
{
    public PremiumAccount(decimal balance) : base(balance) { }
    public override decimal MonthlyFee() => Balance > 10000m ? 0m : 12m;
    public override int FreeTransfers() => 20;
}

public class StudentAccount : Account
{
    public StudentAccount(decimal balance) : base(balance) { }
    public override decimal MonthlyFee() => 0m;
    public override int FreeTransfers() => 5;
}
```

Variant of the same idea, base plus one variant: `ShippingQuote` holds the normal rules, and `ExpressShippingQuote` overrides only the part that differs. The factory picks the subclass. Before, it was a single method: `Total(weight, express) => weight * 2m + (express ? 15m : 0m)`.

```csharp
public class ShippingQuote
{
    protected readonly decimal Weight;
    public ShippingQuote(decimal weight) => Weight = weight;

    public static ShippingQuote Create(decimal weight, bool express) =>
        express ? new ExpressShippingQuote(weight) : new ShippingQuote(weight);

    public decimal Total() => Weight * 2m + Surcharge();
    protected virtual decimal Surcharge() => 0m;
}

public class ExpressShippingQuote : ShippingQuote
{
    public ExpressShippingQuote(decimal weight) : base(weight) { }
    protected override decimal Surcharge() => base.Surcharge() + 15m;
}
```

## C# notes
- A `switch` on a type code becomes `abstract` or `virtual` members, or an interface, depending on whether the cases share code.
- The factory is the one place that still switches on the code. Keep it small and cover it with a test for every value, including the unknown one.
- If the type code is persisted or serialized, keep it as data and map it in the factory.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Each moved branch has a test that fails if the override is removed (if you used the optional throw in step 5, the base method throws until the last branch is moved).
