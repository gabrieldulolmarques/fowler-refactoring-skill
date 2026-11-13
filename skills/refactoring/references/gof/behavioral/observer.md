# Observer

Gamma et al. (1995), ch. 5, p. 293. Also known as: Dependents, Publish-Subscribe. Category: object behavioral.

## Intent
Let one object (the subject) announce its changes to any number of dependents (the observers) without knowing who they are or what they do with the news.

## When it pays off
- One aspect of an abstraction depends on another, and you want to vary and reuse them separately (a sensor and the screens that show it).
- A change in one object must reach others, and the number of receivers is unknown or changes at run time.
- The subject should not assume anything about the receivers, so they can live in higher layers without breaking the layering.
- Benefits: abstract, minimal coupling; broadcast without addressing; observers can be added or removed without touching the subject.
- Liabilities: observers do not know about each other, so one innocent change can trigger a long cascade of updates that is hard to trace. A bare "something changed" signal also forces observers to work out what changed.
- Skip it when there is a single, fixed receiver: a direct call or a delegate parameter is clearer.

## Participants in C#
- **Subject** (`TemperatureSensor`): holds the list of observers and offers attach and detach. In C# this is an `event` field, whose `+=` and `-=` are the attach and detach operations.
- **Observer** (`EventHandler<ReadingChangedEventArgs>`): the updating interface. A delegate type replaces the one-method interface.
- **ConcreteSubject** (`TemperatureSensor`): stores the state of interest and raises the event when it changes.
- **ConcreteObserver** (`Dashboard`, `OverheatAlert`): subscribes to a subject, reads what it needs from the event data or the sender, and keeps its own state consistent.

## Example (C#)
A temperature sensor in an IoT system raises an event on each new reading. A dashboard and an alert rule subscribe independently. Both detach by disposing, so the sensor never keeps them alive longer than needed.

```csharp
using System;
using System.Collections.Generic;

public class ReadingChangedEventArgs : EventArgs
{
    public ReadingChangedEventArgs(string sensorId, double celsius)
    {
        SensorId = sensorId;
        Celsius = celsius;
    }

    public string SensorId { get; }
    public double Celsius { get; }
}

public class TemperatureSensor
{
    private double _celsius;

    public TemperatureSensor(string id) => Id = id;

    public string Id { get; }

    // Subject side: subscribers attach with += and detach with -=.
    public event EventHandler<ReadingChangedEventArgs>? ReadingChanged;

    public void Report(double celsius)
    {
        if (celsius == _celsius) return;   // no change, no notification
        _celsius = celsius;                // state is consistent before notifying
        ReadingChanged?.Invoke(this, new ReadingChangedEventArgs(Id, celsius));
    }
}

public class Dashboard : IDisposable
{
    private readonly TemperatureSensor _sensor;
    private readonly Dictionary<string, double> _latest = new();

    public Dashboard(TemperatureSensor sensor)
    {
        _sensor = sensor;
        _sensor.ReadingChanged += OnReading;
    }

    public double? Latest(string sensorId) => _latest.TryGetValue(sensorId, out var v) ? v : null;

    private void OnReading(object? sender, ReadingChangedEventArgs e) => _latest[e.SensorId] = e.Celsius;

    public void Dispose() => _sensor.ReadingChanged -= OnReading;   // matches the +=
}

public class OverheatAlert : IDisposable
{
    private readonly TemperatureSensor _sensor;
    private readonly double _limit;

    public OverheatAlert(TemperatureSensor sensor, double limit)
    {
        _sensor = sensor;
        _limit = limit;
        _sensor.ReadingChanged += OnReading;
    }

    public bool Tripped { get; private set; }

    private void OnReading(object? sender, ReadingChangedEventArgs e)
    {
        if (e.Celsius > _limit) Tripped = true;
    }

    public void Dispose() => _sensor.ReadingChanged -= OnReading;
}

public static class Program
{
    public static void Main()
    {
        var sensor = new TemperatureSensor("freezer-1");
        using var dashboard = new Dashboard(sensor);
        using var alert = new OverheatAlert(sensor, limit: -10);

        sensor.Report(-18);
        sensor.Report(-5);

        Console.WriteLine($"{dashboard.Latest("freezer-1")} {alert.Tripped}");   // -5 True
    }
}
```

## Variations
- **Where observers are stored.** A list inside each subject is simplest. If there are many subjects and few observers, a shared lookup from subject to observers saves memory at the cost of slower access.
- **Several subjects per observer.** The update carries the sender (the `sender` argument of `EventHandler`), so one handler can tell which subject fired.
- **Who triggers the notification.** Either the state-changing methods notify themselves (clients cannot forget, but a burst of changes causes a burst of updates), or the client calls a notify method after a batch (fewer updates, but easy to forget).
- **Push or pull.** Push sends the details in the event data (the example does). Pull sends almost nothing and the observer reads the subject. Push couples the subject to what observers need; pull can make observers do extra work.
- **Interest by event type.** Expose several events (`ReadingChanged`, `Offline`) or a topic filter so that observers receive only what they asked for.
- **Self-consistent state first.** Notify as the last step of an operation, after all fields are updated. In a class hierarchy, raise the event from a non-overridable method that calls an overridable step, so a subclass cannot notify halfway.
- **A change manager.** When many subjects and observers depend on each other, a separate object can collect changes and notify each observer once. This is a mediator for updates.
- **Subject going away.** The subject can raise a final event so observers drop their reference.

## Risks and C# alternatives
- Use the language feature: `event EventHandler<T>` for subject and observer, and `Action<T>` or a plain delegate when no event data type is needed. Write your own `ISubject`/`IObserver` pair only when you need ordering, filtering or per-subscriber state. `IObservable<T>`/`IObserver<T>` exist in the base library and suit streams that also complete or fail.
- **Every `+=` needs a matching `-=`.** The subject holds a strong reference to each handler's target. A long-lived subject (a sensor, a singleton service, a static event) keeps every subscriber alive after the owner is done with it: a memory leak, and the dead object still receives calls. Unsubscribe in `Dispose`, in a lifecycle hook or when the view closes. Be wary of lambdas, which cannot be detached unless you keep the delegate in a variable.
- **Handlers run synchronously**, on the thread that raised the event, one after another, before the raising call returns. A slow handler slows the subject; an exception in one handler stops the remaining ones and surfaces at the raiser. Keep handlers short, catch inside them, or hand the work to a queue or a `Channel<T>`. An `async void` handler returns at its first `await`, so the subject cannot wait for it or see its exceptions.
- Handlers can attach, detach or change the subject while the event is being raised. `?.Invoke` copies the delegate, so a subscription change does not corrupt the call in progress, but a handler removed during the call may still be called once.
- On multiple threads, the delegate copy is safe, but the handlers themselves run on the raising thread. Marshal to the right context (a UI thread, for example) in the handler.
- Cascades: if a handler changes the subject, or another subject that feeds back, you can get loops. Document which operations notify.

## Related patterns
- [Mediator](mediator.md): a change manager that holds the subject-observer relations acts as a mediator. Observer spreads the communication across objects; Mediator centralizes it in one.
- [Singleton](../creational/singleton.md): a change manager is often unique and global, but pass it in rather than reaching for a global.

## Verification
- The subject compiles and runs with zero subscribers, and its code names no concrete observer type.
- Adding a new observer needs no change to the subject or to other observers.
- Every subscription has an unsubscription on a path that actually runs; after dispose, the subject's handler list no longer references the observer.
- The subject is in a consistent state at the moment each notification is raised, and the operations that notify are documented.
