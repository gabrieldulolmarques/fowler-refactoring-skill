# Replace Hard-Coded Notifications with Observer

Kerievsky (2004), ch. 8, p. 236. Direction: to, towards. Pattern: Observer (GoF, p. 293).

## When to use
Smells: —.

- A class (the notifier) holds a direct reference to one other class (the receiver) and calls it whenever something happens. For exactly one receiver that coupling is fine, and it is the right starting point.
- A second party now needs to hear about the same events, or the receiver should be a different class in some setups. Subclasses that exist only to wire a particular receiver into the base class are the usual symptom.
- With an observer interface, the subject knows only that something is listening, never what. Any class that implements the interface can subscribe.
- Do not introduce it early. A plain hard-coded call is simpler and you can evolve to Observer when the second listener really arrives.
- Watch for two problems. Cascading notifications (an observer that is also a subject, which notifies others, and so on) are hard to debug; consider a Mediator instead. Leaks happen when a long-lived subject keeps a reference to an observer that should be gone, so every subscribe needs a matching unsubscribe.

## Mechanics
Terms: the notifier is the class that calls the receiver; the receiver is the class being called. After the refactoring the notifier's superclass is the subject, and each receiver is an observer.

1. If the notifier does custom work on behalf of its receiver (formatting, deciding, translating) instead of only notifying, move that work into the receiver with Move Function ([move-function.md](../moving-features/move-function.md)). Afterward the notifier's methods only pass the event on. Do this for every notifier. Compile and test.
2. Create the observer interface by extracting an interface from a receiver, keeping only the methods its notifier calls (Extract Interface, 1st ed. only). If other notifiers call receiver methods missing from the interface, add them so one interface fits all receivers. Compile.
3. Make every receiver implement the interface, and make every notifier talk to its receiver only through it. Each receiver is now an observer. Compile and test.
4. For one notifier, move its notification methods up to its superclass with Pull Up Method ([pull-up-method.md](../inheritance/pull-up-method.md)), including the field that holds the observer and the code that sets it. The superclass is now the subject. Repeat for every notifier. Compile.
5. Change each observer to register with the subject directly, not with the notifier, then delete the notifier subclass. Compile and test.
6. Change the subject to hold a collection of observers instead of one: add a subscribe method (and, if observers can leave, an unsubscribe method), and make each notification go to every observer in the collection. Compile and test.
7. Make every subscription pair with an unsubscription at the right moment (when the observer is disposed, closed or replaced), and iterate over a copy of the collection when notifying so an observer that unsubscribes inside its callback does not break the loop.

## Example
Before: `PaymentProcessor` decides the outcome of a charge. `DashboardPaymentProcessor` is a subclass whose only job is to report each charge to one `PaymentDashboard`, and it also builds the text line the dashboard shows.

```csharp
using System.Collections.Generic;

public record ChargeResult(string Account, decimal Amount, bool Approved);

public class PaymentProcessor
{
    public ChargeResult Charge(string account, decimal amount)
    {
        var result = new ChargeResult(account, amount, amount <= 1000m);
        OnCharged(result);
        return result;
    }

    protected virtual void OnCharged(ChargeResult result) { }
}

public class PaymentDashboard
{
    public List<string> Lines { get; } = new();
    public void Add(string line) => Lines.Add(line);
}

public class DashboardPaymentProcessor : PaymentProcessor
{
    private readonly PaymentDashboard _dashboard;
    public DashboardPaymentProcessor(PaymentDashboard dashboard) => _dashboard = dashboard;

    protected override void OnCharged(ChargeResult r)
    {
        var line = $"{r.Account}: {r.Amount:F2} {(r.Approved ? "approved" : "declined")}";
        _dashboard.Add(line);
    }
}
```

After, classic form: the formatting moved to the dashboard (step 1), `IChargeObserver` was extracted (steps 2 and 3), the notification moved up and the subclass was deleted (steps 4 and 5), and the subject now keeps a list (step 6). A second observer, `FraudMonitor`, subscribes without any change to `PaymentProcessor`.

```csharp
using System.Collections.Generic;

public record ChargeResult(string Account, decimal Amount, bool Approved);

public interface IChargeObserver
{
    void Charged(ChargeResult result);
}

public class PaymentProcessor
{
    private readonly List<IChargeObserver> _observers = new();

    public void Subscribe(IChargeObserver observer) => _observers.Add(observer);
    public void Unsubscribe(IChargeObserver observer) => _observers.Remove(observer);

    public ChargeResult Charge(string account, decimal amount)
    {
        var result = new ChargeResult(account, amount, amount <= 1000m);
        foreach (var observer in _observers.ToArray())
            observer.Charged(result);
        return result;
    }
}

public class PaymentDashboard : IChargeObserver
{
    public List<string> Lines { get; } = new();

    public void Charged(ChargeResult r) =>
        Lines.Add($"{r.Account}: {r.Amount:F2} {(r.Approved ? "approved" : "declined")}");
}

public class FraudMonitor : IChargeObserver
{
    public int Declines { get; private set; }
    public void Charged(ChargeResult r) { if (!r.Approved) Declines++; }
}

// Wiring and teardown, always as a pair:
//   var processor = new PaymentProcessor();
//   var dashboard = new PaymentDashboard();
//   processor.Subscribe(dashboard);
//   processor.Charge("acc-1", 50m);
//   processor.Unsubscribe(dashboard);
```

After, idiomatic C#: the same design with an event instead of an interface and two methods. The observer interface becomes the delegate type `EventHandler<ChargeResult>`, and the list, `Subscribe` and `Unsubscribe` become `event`, `+=` and `-=`.

```csharp
using System;
using System.Collections.Generic;

public record ChargeResult(string Account, decimal Amount, bool Approved);

public class PaymentProcessor
{
    public event EventHandler<ChargeResult>? Charged;

    public ChargeResult Charge(string account, decimal amount)
    {
        var result = new ChargeResult(account, amount, amount <= 1000m);
        Charged?.Invoke(this, result);
        return result;
    }
}

public class PaymentDashboard
{
    public List<string> Lines { get; } = new();

    public void Attach(PaymentProcessor processor) => processor.Charged += OnCharged;
    public void Detach(PaymentProcessor processor) => processor.Charged -= OnCharged;

    private void OnCharged(object? sender, ChargeResult r) =>
        Lines.Add($"{r.Account}: {r.Amount:F2} {(r.Approved ? "approved" : "declined")}");
}
```

## C# notes
- The idiomatic form is a C# `event` (`event EventHandler<T>`, or `Action<T>` for simple cases). Use an observer interface only when an observer needs several different callbacks or you want to pass it around as a unit.
- Every `+=` needs a matching `-=`, and the subject often outlives the subscriber, so an event handler that is never removed keeps the subscriber alive. Unsubscribe in `Dispose`, in a close method, or when the observer is replaced. For a subscriber that implements `IDisposable`, put the `-=` there.
- Subscribing a lambda or anonymous method is easy, but `-=` with a new, textually identical lambda does not remove it. Keep the delegate in a field if you will need to unsubscribe.
- Only the declaring class can raise an `event`; outside code can only `+=` and `-=`. That is usually what you want. Use `?.Invoke` so an event with no subscribers does not throw.
- Handlers run synchronously, in subscription order, on the caller's thread. If one throws, the rest are skipped, and a slow handler slows down `Charge`. Keep handlers short, or catch and report inside the raising method if one bad observer must not stop the others.
- A handler that unsubscribes (or subscribes) during notification is safe with events, because delegates are immutable and `Invoke` works on a snapshot. With the manual list version, iterate over a copy, as above.
- If the subject must live much longer than observers and you cannot guarantee unsubscription, a weak-event pattern or a different design (polling, a message bus) is safer than relying on discipline.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- A test with two observers checks that both receive each event, in the expected order, and that an observer sees nothing after it unsubscribes.
- Search for each `Subscribe` or `+=`: every one has a reachable `Unsubscribe` or `-=`. After the last observer is gone, the subject holds no reference to it.
