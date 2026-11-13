# Replace Function with Command

Fowler (2018), ch. 11, p. 337. Formerly / aka: Replace Method with Method Object. Inverse:
Replace Command with Function ([replace-command-with-function.md](replace-command-with-function.md)).

## When to use
Smell: Long Function. The typical trigger is a function whose locals and parameters are so
intertwined that Extract Function would need long parameter lists or return several values.
Turning the function into an object makes those locals fields, so the pieces can share them.

A command also helps when the operation needs more than a call can offer: undo, being queued or
logged, parameters supplied in stages, subclass or hook customization, or tests aimed at its
inner steps.

Do not use it by default. A command is extra structure; a plain function (or delegate) is the
better choice most of the time. Reach for a command only when a simpler device cannot give you
what you need.

## Mechanics
1. Create an empty class named after the function (follow the language's naming convention for
   commands).
2. Apply Move Function ([move-function.md](../moving-features/move-function.md)) to move the function body into the class as a
   single method. Use the convention's name for it, or a generic one such as `Execute`.
   Leave the original function in place as a forwarder that creates the command and calls it;
   keep it until the end.
3. Compile and test.
4. Move the arguments to the constructor one at a time: add a field and a constructor
   parameter, pass it from the forwarder, remove it from the method's parameter list and
   update its uses in the body. Compile and test after each one.

**Beyond the book:** to break the body up, as the example does, promote the local variables to fields one at a time, compiling and testing after each. Then apply Extract Function ([extract-function.md](../first-set/extract-function.md)) to the body; the new methods read and write the fields directly.

## Example
Before: a function that prices a campaign, with several interacting locals.

```csharp
public class Campaign
{
    public Campaign(string channel, int recipients, int optedOut)
    {
        Channel = channel;
        Recipients = recipients;
        OptedOut = optedOut;
    }

    public string Channel { get; }
    public int Recipients { get; }
    public int OptedOut { get; }
}

public class Account
{
    public Account(string region, bool isPrepaid)
    {
        Region = region;
        IsPrepaid = isPrepaid;
    }

    public string Region { get; }
    public bool IsPrepaid { get; }
}

public interface IRateTable
{
    decimal PricePerMessage(string channel);
    decimal TaxRate(string region);
}

public static class Billing
{
    public static decimal CampaignCost(Campaign campaign, Account account, IRateTable rates)
    {
        int deliverable = campaign.Recipients - campaign.OptedOut;
        decimal subtotal = deliverable * rates.PricePerMessage(campaign.Channel);
        decimal discount = 0m;
        if (deliverable > 10000)
            discount += subtotal * 0.05m;
        if (account.IsPrepaid)
            discount += subtotal * 0.02m;
        decimal taxable = subtotal - discount;
        decimal tax = taxable * rates.TaxRate(account.Region);
        return taxable + tax;
    }
}
```

After step 4 (the forwarder stays, the command owns the arguments):

```csharp
public static class Billing
{
    public static decimal CampaignCost(Campaign campaign, Account account, IRateTable rates)
        => new CampaignCostCalculator(campaign, account, rates).Execute();
}

public class CampaignCostCalculator
{
    private readonly Campaign _campaign;
    private readonly Account _account;
    private readonly IRateTable _rates;

    public CampaignCostCalculator(Campaign campaign, Account account, IRateTable rates)
    {
        _campaign = campaign;
        _account = account;
        _rates = rates;
    }

    public decimal Execute()
    {
        int deliverable = _campaign.Recipients - _campaign.OptedOut;
        decimal subtotal = deliverable * _rates.PricePerMessage(_campaign.Channel);
        decimal discount = 0m;
        if (deliverable > 10000)
            discount += subtotal * 0.05m;
        if (_account.IsPrepaid)
            discount += subtotal * 0.02m;
        decimal taxable = subtotal - discount;
        decimal tax = taxable * _rates.TaxRate(_account.Region);
        return taxable + tax;
    }
}
```

After promoting the locals and extracting (locals promoted to fields, then pieces extracted):

```csharp
public class CampaignCostCalculator
{
    private readonly Campaign _campaign;
    private readonly Account _account;
    private readonly IRateTable _rates;
    private int _deliverable;
    private decimal _subtotal;
    private decimal _discount;

    public CampaignCostCalculator(Campaign campaign, Account account, IRateTable rates)
    {
        _campaign = campaign;
        _account = account;
        _rates = rates;
    }

    public decimal Execute()
    {
        _deliverable = _campaign.Recipients - _campaign.OptedOut;
        _subtotal = _deliverable * _rates.PricePerMessage(_campaign.Channel);
        ApplyDiscounts();
        decimal taxable = _subtotal - _discount;
        return taxable + taxable * _rates.TaxRate(_account.Region);
    }

    private void ApplyDiscounts()
    {
        _discount = 0m;
        if (_deliverable > 10000)
            _discount += _subtotal * 0.05m;
        if (_account.IsPrepaid)
            _discount += _subtotal * 0.02m;
    }
}
```

Behavior is the same at every stage. Note that `Execute` now mutates fields, so a command
instance can be run again, since `Execute` resets every field it reads, but it is not thread-safe.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
