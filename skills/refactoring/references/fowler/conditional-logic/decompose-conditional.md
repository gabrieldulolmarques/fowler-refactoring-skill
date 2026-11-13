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
using System;

public class Parcel
{
    public decimal WeightKg { get; }
    public int Zone { get; }
    public decimal Subtotal { get; }

    public Parcel(decimal weightKg, int zone, decimal subtotal)
    {
        WeightKg = weightKg;
        Zone = zone;
        Subtotal = subtotal;
    }
}

public class Campaign
{
    public DateTime Start { get; }
    public DateTime End { get; }
    public decimal MinimumSubtotal { get; }
    public decimal FlatRate { get; }

    public Campaign(DateTime start, DateTime end, decimal minimumSubtotal, decimal flatRate)
    {
        Start = start;
        End = end;
        MinimumSubtotal = minimumSubtotal;
        FlatRate = flatRate;
    }
}

public class ShippingCalculator
{
    public decimal Cost(Parcel parcel, Campaign campaign, DateTime today)
    {
        decimal cost;
        if (today >= campaign.Start && today <= campaign.End && parcel.Subtotal >= campaign.MinimumSubtotal)
            cost = campaign.FlatRate;
        else
            cost = 4m + parcel.Zone * 1.5m + parcel.WeightKg * 0.8m;
        return cost;
    }
}
```

After:

```csharp
public class ShippingCalculator
{
    public decimal Cost(Parcel parcel, Campaign campaign, DateTime today)
    {
        return QualifiesForCampaign(parcel, campaign, today)
            ? CampaignRate(campaign)
            : ZoneAndWeightRate(parcel);
    }

    private static bool QualifiesForCampaign(Parcel parcel, Campaign campaign, DateTime today) =>
        today >= campaign.Start
        && today <= campaign.End
        && parcel.Subtotal >= campaign.MinimumSubtotal;

    private static decimal CampaignRate(Campaign campaign) =>
        campaign.FlatRate;

    private static decimal ZoneAndWeightRate(Parcel parcel) =>
        4m + parcel.Zone * 1.5m + parcel.WeightKg * 0.8m;
}
```

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
