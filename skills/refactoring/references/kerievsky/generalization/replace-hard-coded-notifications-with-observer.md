# Replace Hard-Coded Notifications with Observer

Kerievsky (2004), ch. 8, p. 236. Pattern: Observer. Direction: to, towards.

## When to use
Smells: —.

- A class (the notifier) holds a direct reference to one other class (the receiver) and calls it whenever something happens. For exactly one receiver that coupling is fine, and it is the right starting point.
- A second party now needs to hear about the same events, or the receiver should be a different class in some setups. Subclasses that exist only to wire a particular receiver into the base class are the usual symptom.
- With an observer interface, the subject knows only that something is listening, never what. Any class that implements the interface can subscribe.
- Do not introduce it early. A plain hard-coded call is simpler and you can evolve to Observer when the second listener really arrives.
- Watch for two problems. Cascading notifications (an observer that is also a subject, which notifies others, and so on) are hard to debug; consider a Mediator instead. Leaks happen when a long-lived subject keeps a reference to an observer that should be gone, so every subscribe needs a matching unsubscribe.

## Mechanics
Terms: the notifier is the class that calls the receiver; the receiver is the class being called. After the refactoring the notifier's superclass is the subject, and each receiver is an observer.

1. If the notifier does custom work on behalf of its receiver (formatting, deciding, translating) instead of only notifying, move that work into the receiver with Move Function ([move-function.md](../../fowler/moving-features/move-function.md)). Afterward the notifier's methods only pass the event on. Do this for every notifier. Compile and test.
2. Create the observer interface by extracting an interface from a receiver, keeping only the methods its notifier calls (Extract Interface, 1st ed. only). If other notifiers call receiver methods missing from the interface, add them so one interface fits all receivers. Compile.
3. Make every receiver implement the interface, and make every notifier talk to its receiver only through it. Each receiver is now an observer. Compile and test.
4. For one notifier, move its notification methods up to its superclass with Pull Up Method ([pull-up-method.md](../../fowler/inheritance/pull-up-method.md)), including the field that holds the observer and the code that sets it. The superclass is now the subject. Repeat for every notifier. Compile.
5. Change each observer to register with the subject directly, not with the notifier, then delete the notifier subclass. Compile and test.
6. Change the subject to hold a collection of observers instead of one: add a subscribe method (and, if observers can leave, an unsubscribe method), and make each notification go to every observer in the collection. Compile and test.
7. Make every subscription pair with an unsubscription at the right moment (when the observer is disposed, closed or replaced), and iterate over a copy of the collection when notifying so an observer that unsubscribes inside its callback does not break the loop.

## Example
Before: `TokenMeter` measures the token usage of a conversation against its budget. `DashboardTokenMeter` is a subclass whose only job is to report each measurement to one `UsageDashboard`, and it also builds the text line the dashboard shows.

```csharp
using System.Collections.Generic;

public class UsageReport
{
    public string Conversation { get; }
    public int Tokens { get; }
    public bool OverBudget { get; }
    public UsageReport(string conversation, int tokens, bool overBudget)
    {
        Conversation = conversation;
        Tokens = tokens;
        OverBudget = overBudget;
    }
}

public class TokenMeter
{
    public UsageReport Record(string conversation, int tokens)
    {
        var report = new UsageReport(conversation, tokens, tokens > 4000);
        OnRecorded(report);
        return report;
    }

    protected virtual void OnRecorded(UsageReport report) { }
}

public class UsageDashboard
{
    public List<string> Lines { get; } = new();
    public void Add(string line) => Lines.Add(line);
}

public class DashboardTokenMeter : TokenMeter
{
    private readonly UsageDashboard _dashboard;
    public DashboardTokenMeter(UsageDashboard dashboard) => _dashboard = dashboard;

    protected override void OnRecorded(UsageReport r)
    {
        var line = $"{r.Conversation}: {r.Tokens} tokens {(r.OverBudget ? "over budget" : "ok")}";
        _dashboard.Add(line);
    }
}
```

After, classic form: the formatting moved to the dashboard (step 1), `IUsageObserver` was extracted (steps 2 and 3), the notification moved up and the subclass was deleted (steps 4 and 5), and the subject now keeps a list (step 6). A second observer, `BudgetAlarm`, subscribes without any change to `TokenMeter`.

```csharp
using System.Collections.Generic;

public class UsageReport
{
    public string Conversation { get; }
    public int Tokens { get; }
    public bool OverBudget { get; }
    public UsageReport(string conversation, int tokens, bool overBudget)
    {
        Conversation = conversation;
        Tokens = tokens;
        OverBudget = overBudget;
    }
}

public interface IUsageObserver
{
    void Recorded(UsageReport report);
}

public class TokenMeter
{
    private readonly List<IUsageObserver> _observers = new();

    public void Subscribe(IUsageObserver observer) => _observers.Add(observer);
    public void Unsubscribe(IUsageObserver observer) => _observers.Remove(observer);

    public UsageReport Record(string conversation, int tokens)
    {
        var report = new UsageReport(conversation, tokens, tokens > 4000);
        foreach (var observer in _observers.ToArray())
            observer.Recorded(report);
        return report;
    }
}

public class UsageDashboard : IUsageObserver
{
    public List<string> Lines { get; } = new();

    public void Recorded(UsageReport r) =>
        Lines.Add($"{r.Conversation}: {r.Tokens} tokens {(r.OverBudget ? "over budget" : "ok")}");
}

public class BudgetAlarm : IUsageObserver
{
    public int Overruns { get; private set; }
    public void Recorded(UsageReport r) { if (r.OverBudget) Overruns++; }
}

// Wiring and teardown, always as a pair:
//   var meter = new TokenMeter();
//   var dashboard = new UsageDashboard();
//   meter.Subscribe(dashboard);
//   meter.Record("chat-1", 1200);
//   meter.Unsubscribe(dashboard);
```

After, idiomatic C#: the same design with an event instead of an interface and two methods. The observer interface becomes the delegate type `EventHandler<UsageReport>`, and the list, `Subscribe` and `Unsubscribe` become `event`, `+=` and `-=`.

```csharp
using System;
using System.Collections.Generic;

public class UsageReport
{
    public string Conversation { get; }
    public int Tokens { get; }
    public bool OverBudget { get; }
    public UsageReport(string conversation, int tokens, bool overBudget)
    {
        Conversation = conversation;
        Tokens = tokens;
        OverBudget = overBudget;
    }
}

public class TokenMeter
{
    public event EventHandler<UsageReport>? Recorded;

    public UsageReport Record(string conversation, int tokens)
    {
        var report = new UsageReport(conversation, tokens, tokens > 4000);
        Recorded?.Invoke(this, report);
        return report;
    }
}

public class UsageDashboard
{
    public List<string> Lines { get; } = new();

    public void Attach(TokenMeter meter) => meter.Recorded += OnRecorded;
    public void Detach(TokenMeter meter) => meter.Recorded -= OnRecorded;

    private void OnRecorded(object? sender, UsageReport r) =>
        Lines.Add($"{r.Conversation}: {r.Tokens} tokens {(r.OverBudget ? "over budget" : "ok")}");
}
```

## C# notes
- The idiomatic form is a C# `event` (`event EventHandler<T>`, or `Action<T>` for simple cases). Use an observer interface only when an observer needs several different callbacks or you want to pass it around as a unit.
- Every `+=` needs a matching `-=`, and the subject often outlives the subscriber, so an event handler that is never removed keeps the subscriber alive. Unsubscribe in `Dispose`, in a close method, or when the observer is replaced. For a subscriber that implements `IDisposable`, put the `-=` there.
- Subscribing a lambda or anonymous method is easy, but `-=` with a new, textually identical lambda does not remove it. Keep the delegate in a field if you will need to unsubscribe.
- Only the declaring class can raise an `event`; outside code can only `+=` and `-=`. That is usually what you want. Use `?.Invoke` so an event with no subscribers does not throw.
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- A test with two observers checks that both receive each event, in the expected order, and that an observer sees nothing after it unsubscribes.
- Search for each `Subscribe` or `+=`: every one has a reachable `Unsubscribe` or `-=`. After the last observer is gone, the subject holds no reference to it.
