# Replace Subclass with Delegate

Fowler (2018), ch. 12, p. 381. Formerly / aka: —. Inverse: —.
Remove Subclass and Collapse Hierarchy go the other way for simple cases.

## When to use
Smells: Insider Trading, Refused Bequest, Middle Man.

- Inheritance gives one axis of variation only. If the same class must also vary by a second
  criterion, one of the two must become a delegate.
- The variant must change during the object's life (a regular order becomes a priority order),
  and replacing the object is not practical because many places hold a reference to it.
- The subclass and superclass are so entangled that changing the parent keeps breaking the
  child, especially across modules or teams.

**Beyond the book:** if inheritance fits well and none of the above applies, keep it. The result
has dispatch logic and a two-way reference, so the refactoring alone rarely makes the code
simpler; the payoff is the freedom it buys. Prefer inheritance first and move to a delegate
when it starts to hurt.

## Mechanics
1. If many callers construct the subclass, wrap construction first with Replace Constructor
   with Factory Function ([replace-constructor-with-factory-function.md](../refactoring-apis/replace-constructor-with-factory-function.md)).
2. Create an empty delegate class. Its constructor takes the data only the subclass uses and,
   usually, a back-reference to the host (the superclass instance).
3. Add a field to the superclass that holds the delegate (null when there is none).
4. Make the creation code (factory or constructor) build the delegate and store it in that
   field.
5. Pick one method of the subclass and move it to the delegate with Move Function
   ([move-function.md](../moving-features/move-function.md)). Reach host data through the back-reference; move data that only
   the subclass uses into the delegate. Leave a forwarding method in the subclass for now.
   Test.
6. If the superclass method has callers outside the hierarchy, give the superclass method
   dispatch logic: use the delegate when present, otherwise the original behavior. If the
   subclass method called the base implementation, either extract the base calculation into
   its own method that the delegate can call, or turn the delegate method into an extension of
   the base result (the host passes its result in). Do not call the host's own virtual
   method from the delegate: that recurses forever. If the method exists only in the subclass,
   dispatch with a sensible default for the no-delegate case. If there is more than one
   subclass and the delegates start duplicating code, apply Extract Superclass
   ([extract-superclass.md](extract-superclass.md)) on the delegates. Test.
7. If the method has no outside callers, just remove the subclass method (Remove Dead Code,
   [remove-dead-code.md](../moving-features/remove-dead-code.md)). Test.
8. Repeat steps 5 to 7 for every member of the subclass.
9. Change every construction of the subclass to build the superclass. Test.
10. Delete the now empty subclass.

**Beyond the book:** when the delegates share a superclass, creating a delegate in every case lets the host dispatch without a null check, and the default delegate holds the default behavior. Do not branch on the delegate's concrete type.

## Example
Before: student subscriptions are a subclass.

```csharp
public class Subscription
{
    protected readonly decimal BasePrice;

    public Subscription(decimal basePrice) => BasePrice = basePrice;

    public virtual decimal MonthlyPrice => BasePrice;
    public virtual bool AllowsOfflineDownloads => BasePrice >= 10m;
}

public class StudentSubscription : Subscription
{
    private readonly decimal _discountRate;

    public StudentSubscription(decimal basePrice, decimal discountRate) : base(basePrice)
        => _discountRate = discountRate;

    public override decimal MonthlyPrice => decimal.Round(base.MonthlyPrice * (1 - _discountRate), 2);
    public override bool AllowsOfflineDownloads => true;
    public decimal SavedAmount => BasePrice - MonthlyPrice;
}
```

After: the student behavior lives in a delegate, so a subscription can become a student one at
runtime and the base class stays free for another use of inheritance.

```csharp
// fragment
public class Subscription
{
    private StudentDelegate? _student;

    internal decimal BasePrice { get; }

    private Subscription(decimal basePrice) => BasePrice = basePrice;

    public static Subscription Create(decimal basePrice) => new Subscription(basePrice);

    public static Subscription CreateStudent(decimal basePrice, decimal discountRate)
    {
        var subscription = new Subscription(basePrice);
        subscription.BecomeStudent(discountRate);
        return subscription;
    }

    public void BecomeStudent(decimal discountRate)
        => _student = new StudentDelegate(this, discountRate);

    public decimal MonthlyPrice
    {
        get
        {
            var result = BasePrice;
            return _student is null ? result : _student.ExtendPrice(result);
        }
    }

    public bool AllowsOfflineDownloads
        => _student is null ? BasePrice >= 10m : _student.AllowsOfflineDownloads;

    public decimal? SavedAmount => _student?.SavedAmount;
}

internal class StudentDelegate
{
    private readonly Subscription _host;
    private readonly decimal _discountRate;

    public StudentDelegate(Subscription host, decimal discountRate)
    {
        _host = host;
        _discountRate = discountRate;
    }

    public decimal ExtendPrice(decimal basePrice) => decimal.Round(basePrice * (1 - _discountRate), 2);
    public bool AllowsOfflineDownloads => true;
    public decimal SavedAmount => _host.BasePrice - _host.MonthlyPrice;
}
```

Behavior is unchanged for callers that go through `Subscription.Create` and
`Subscription.CreateStudent`; the `StudentSubscription` class is gone.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Tests cover both variants of every moved method, including the base-call case and a switch
  of variant at runtime if the delegate is meant to be replaceable.
- No caller still constructs the removed subclass or checks the delegate's concrete type.
