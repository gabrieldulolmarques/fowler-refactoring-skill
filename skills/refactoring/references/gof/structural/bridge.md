# Bridge

Gamma et al. (1995), ch. 4, p. 151. Also known as: Handle/Body. Category: object structural.

## Intent
Split an abstraction from its implementation into two hierarchies joined by a reference, so each can be extended on its own.

## When it pays off
- You have two independent dimensions of variation (for example what a message means and how it is delivered), and subclassing for every pair would multiply classes (`UrgentEmail`, `UrgentPush`, `ReminderEmail`, ...).
- The implementation should be chosen or swapped at runtime, or hidden from client code.
- Benefits: implementation and abstraction can be extended separately, clients depend only on the abstraction, and the implementation can change without touching them.
- Liability: one more layer of indirection, and the split must be made at the right seam. It is designed in from the start; it is not a fix for two classes that happen to be incompatible.
- Skip it when there is one implementation and no sign of more. A plain interface is enough then, and the bridge can come later.

## Participants in C#
- **Abstraction** (`Notification`): an abstract class that holds a reference to the implementor and defines the high-level operation in terms of it.
- **RefinedAbstraction** (`SecurityAlert`, `DeliveryReminder`): subclasses that vary the high-level behavior.
- **Implementor** (`IChannel`): interface with the primitive operations the abstraction needs. It need not look like the abstraction's interface.
- **ConcreteImplementor** (`EmailChannel`, `PushChannel`, `WebhookChannel`): classes that implement `IChannel` for a specific delivery method.

## Example (C#)
Notifications have kinds (security alert, delivery reminder) and channels (e-mail, push, webhook). Each kind builds its text and sends it through whatever channel it was given. Adding a channel or a kind touches one place.

```csharp
using System;

public interface IChannel
{
    void Send(string recipient, string title, string body);
}

public class EmailChannel : IChannel
{
    public void Send(string recipient, string title, string body) =>
        Console.WriteLine($"[email to {recipient}] {title}: {body}");
}

public class PushChannel : IChannel
{
    public void Send(string recipient, string title, string body) =>
        Console.WriteLine($"[push to device of {recipient}] {title}");
}

public class WebhookChannel : IChannel
{
    private readonly string _url;

    public WebhookChannel(string url) => _url = url;

    public void Send(string recipient, string title, string body) =>
        Console.WriteLine($"[POST {_url}] {{\"to\":\"{recipient}\",\"title\":\"{title}\"}}");
}

public abstract class Notification
{
    protected IChannel Channel { get; }

    protected Notification(IChannel channel) => Channel = channel;

    public abstract void Notify(string recipient);
}

public class SecurityAlert : Notification
{
    private readonly string _location;

    public SecurityAlert(IChannel channel, string location) : base(channel) => _location = location;

    public override void Notify(string recipient) =>
        Channel.Send(recipient, "New sign-in", $"A sign-in from {_location} was detected.");
}

public class DeliveryReminder : Notification
{
    private readonly DateTime _eta;

    public DeliveryReminder(IChannel channel, DateTime eta) : base(channel) => _eta = eta;

    public override void Notify(string recipient) =>
        Channel.Send(recipient, "Your package arrives soon", $"Expected at {_eta:HH:mm}.");
}

public static class Program
{
    public static void Main()
    {
        Notification a = new SecurityAlert(new EmailChannel(), "Lisbon");
        Notification b = new DeliveryReminder(new PushChannel(), new DateTime(2026, 1, 5, 14, 30, 0));
        Notification c = new SecurityAlert(new WebhookChannel("https://hooks.example/ops"), "Oslo");
        a.Notify("ana");
        b.Notify("ana");
        c.Notify("ops");
    }
}
```

## Variations
- **Single implementor**: when there is only one implementation, the abstract implementor can be dropped. The separation still lets that implementation change without touching clients.
- **Choosing the implementor**: the abstraction can pick it in its constructor from parameters, start with a default and switch later (for example by size or load), or ask a factory so it never names a concrete class. In C# the simplest form is constructor injection, with the choice made at the composition root or by a DI container.
- **Shared implementors**: several abstraction objects can hold the same implementor instance. Implementors are often stateless or thread-safe so that sharing is safe.
- **Back reference**: the implementor may need to report events (a message was rejected) to the abstraction; give it an event or a callback, not the concrete type.

## Risks and C# alternatives
- If the implementor needs only one operation, a delegate (`Action<string, string, string>`) can replace the interface. Keep the interface once it has several members or needs its own state and tests.
- Dependency injection already gives you the bridge for free: the abstraction takes the interface in its constructor. The pattern is mostly about seeing the two axes and keeping them apart.
- Do not let `Notification` subclasses test the channel type (`if (Channel is EmailChannel)`). That voids the decoupling; put the difference into the interface.
- Splitting too early adds interfaces nobody uses. Do it when the second axis shows up, not before.

## Related patterns
- [abstract-factory.md](../creational/abstract-factory.md): can create and configure a particular bridge, so abstractions do not name concrete implementors.
- [adapter.md](adapter.md): looks alike, but it reconciles existing, unrelated classes after the fact. Bridge is a design choice made up front.

## Verification
- Adding a channel needs no change in `Notification` or its subclasses; adding a kind needs no change in channels.
- The number of classes grows as kinds plus channels, not kinds times channels.
- No refined abstraction checks the concrete type of its implementor.
- Tests for a kind use a fake `IChannel` and check what was sent.
