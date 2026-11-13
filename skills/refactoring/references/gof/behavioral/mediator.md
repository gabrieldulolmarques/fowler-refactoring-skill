# Mediator

Gamma et al. (1995), ch. 5, p. 273. Category: object behavioral.

## Intent
Put the rules for how a group of objects interact into one object, so the group's members do not refer to each other. The interaction can then change without touching the members.

## When it pays off
- The way a group of objects talk to each other is clear enough in each case but has grown into a tangle of references that is hard to follow.
- An object is hard to reuse because it knows and talks to many others.
- Behavior spread across several classes should be customizable without a pile of subclasses.
- Benefits: colleagues become reusable on their own, many-to-many links become one-to-many, and the cooperation rules sit in one named place. Changing the rules means changing or replacing the mediator only.
- Liability: the complexity moves into the mediator, which can grow into a monolith. Watch its size.
- Not worth it for two objects, or when a simple event subscription is enough.

## Participants in C#
- **Mediator** (`ISignupMediator`): interface that colleagues use to report changes.
- **ConcreteMediator** (`SignupForm`): knows its colleagues and implements the coordination.
- **Colleague** (`PlanSelector`, `CouponField`, `PayButton`): each knows only the mediator and reports to it instead of calling other colleagues.

## Example (C#)
A SaaS sign-up screen: the choice of plan decides whether a coupon is allowed, and the pay button is enabled only when the form is valid. The widgets do not know each other. One class holds the rules.

```csharp
using System;

public interface ISignupMediator
{
    void Changed(object colleague);
}

public class PlanSelector
{
    private readonly ISignupMediator _mediator;
    private string _plan = "free";

    public PlanSelector(ISignupMediator mediator) => _mediator = mediator;

    public string Plan
    {
        get => _plan;
        set
        {
            _plan = value;
            _mediator.Changed(this);
        }
    }
}

public class CouponField
{
    private readonly ISignupMediator _mediator;
    private string _code = "";

    public CouponField(ISignupMediator mediator) => _mediator = mediator;

    public bool Enabled { get; set; }

    public string Code
    {
        get => _code;
        set
        {
            _code = value;
            _mediator.Changed(this);
        }
    }
}

public class PayButton
{
    public bool Enabled { get; set; }
}

public class SignupForm : ISignupMediator
{
    public PlanSelector Plan { get; }
    public CouponField Coupon { get; }
    public PayButton Pay { get; }

    public SignupForm()
    {
        Plan = new PlanSelector(this);
        Coupon = new CouponField(this);
        Pay = new PayButton();
        Refresh();
    }

    public void Changed(object colleague) => Refresh();

    // All cooperation rules live here.
    private void Refresh()
    {
        bool paid = Plan.Plan != "free";
        Coupon.Enabled = paid;
        if (!paid && Coupon.Code != "") Coupon.Code = "";   // reports back, so guard against looping
        bool couponOk = Coupon.Code == "" || Coupon.Code.StartsWith("PROMO", StringComparison.Ordinal);
        Pay.Enabled = couponOk;
    }
}

public static class Program
{
    public static void Main()
    {
        var form = new SignupForm();
        form.Plan.Plan = "pro";
        form.Coupon.Code = "oops";
        Console.WriteLine(form.Pay.Enabled);   // False
        form.Coupon.Code = "PROMO10";
        Console.WriteLine(form.Pay.Enabled);   // True
    }
}
```

## Variations
- **Omit the abstract mediator.** If colleagues only ever work with one mediator, the interface adds nothing. Keep it when colleagues must be reused with different mediators.
- **How colleagues talk to the mediator.** Either the mediator subscribes to colleague events (the observer way, with C# `event`), or colleagues call a specific method on the mediator and pass themselves, so the mediator knows who changed. Passing the sender is direct and easy to debug. Events keep colleagues free of any mediator reference.
- **Mediator for coordinating updates.** A mediator can sit between a set of sources and a set of listeners to batch notifications and avoid redundant work.

## Risks and C# alternatives
- A mediator that knows everything becomes a god class. Split it by concern (one per screen, per workflow) and keep decisions, not data, in it.
- Re-entrancy: a colleague changed by the mediator may report back and trigger the mediator again. Make the refresh idempotent or guard against loops, as the example does.
- A message bus or event aggregator is a mediator with a generic interface. It decouples more but makes the flow harder to trace. Use it when the participants are many and unknown in advance.
- For simple one-way coupling (a value changes, others react), plain `event`s are lighter than a mediator.
- With dependency injection, give colleagues the mediator interface by constructor, as above.

## Related patterns
- [Facade](../structural/facade.md): also simplifies a group of objects, but its protocol is one-way (clients call the subsystem), while a mediator is multi-directional and colleagues know it.
- [Observer](observer.md): colleagues can notify the mediator through observer notifications.

## Verification
- No colleague class refers to another colleague class, only to the mediator.
- A colleague works in a test with a fake mediator.
- A rule change (a new dependency between widgets) is made in the mediator only.
- The mediator is still a manageable size and does not hold data that belongs to a colleague.
