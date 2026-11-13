# Unify Interfaces with Adapter

Kerievsky (2004), ch. 8, p. 247. Direction: to, towards. Pattern: Adapter (GoF, p. 139).

## When to use
Smells: Alternative Classes with Different Interfaces, Oddball Solution, Duplicated Code.

- Two classes do the same or similar work through different interfaces, and a client that uses both has to be written twice.
- The client would be simpler if both looked the same.
- You cannot just rename or move methods until they match, because one class belongs to a third-party library, to a framework with many other clients, or you lack its source.
- Once both classes sit behind one interface, the duplicated client code can be merged with refactorings such as Form Template Method ([form-template-method.md](form-template-method.md)) or Introduce Polymorphic Creation with Factory Method ([introduce-polymorphic-creation-with-factory-method.md](../creation/introduce-polymorphic-creation-with-factory-method.md)).
- Do not use it when you can change one of the interfaces directly: renaming is cheaper than adding a class.

## Mechanics
The adaptee is the class whose interface the client does not prefer. The adapter is the class that will wrap it.

1. Extract a common interface from the class whose interface the client prefers (Extract Interface, 1st ed. only). If that class has methods taking its own type, change them to take the interface. Compile and test.
2. In the client that uses the adaptee, apply Extract Class ([extract-class.md](../../fowler/encapsulation/extract-class.md)) to create a primitive adapter: a class with an adaptee field, a getter for it, and a constructor (or setter) that receives it.
3. Change the client's fields, locals and parameters of the adaptee type to the adapter type. Each call now first gets the adaptee from the adapter. Compile and test.
4. For each distinct adaptee call in the client, apply Extract Function ([extract-function.md](../../fowler/first-set/extract-function.md)) to make an invocation method that takes the adapter as a parameter and calls the adaptee through it. Compile and test after each.
5. Move each invocation method into the adapter with Move Function ([move-function.md](../../fowler/moving-features/move-function.md)), shaping it like the matching method of the common interface. If the moved body needs a value from the client, pass it in the adapter's constructor, or give the adapter a reference it can query, rather than adding a parameter that would make the signature differ. If a parameter is unavoidable, change the interface method to match. Compile and test; repeat until the adapter has every method of the interface.
6. Declare that the adapter implements the common interface, and change adapter methods that take an adapter to take the interface. Compile and test.
7. Change the client to use the interface everywhere instead of the adapter type. Compile and test. The client now talks to both classes through one type.

## Example
Before: a notifier sends receipts through our own `EmailSender` and, with a separate copy of the logic, through a third-party `SmsGateway` that we cannot change.

```csharp
using System.Collections.Generic;

public record Customer(string Name, string Email, string Phone);
public record SmsMessage(string Number, string Text);

public class EmailSender
{
    public List<string> Sent { get; } = new();
    public void Send(string to, string subject, string body) => Sent.Add($"{to}|{subject}|{body}");
}

// Third party: cannot be changed.
public sealed class SmsGateway
{
    public List<SmsMessage> Outbox { get; } = new();
    public void Transmit(SmsMessage message) => Outbox.Add(message);
}

public class ReceiptNotifier
{
    public void ByEmail(IEnumerable<Customer> customers, EmailSender sender, string orderId)
    {
        foreach (var c in customers)
            sender.Send(c.Email, "Receipt", $"Dear {c.Name}, order {orderId} is paid.");
    }

    public void BySms(IEnumerable<Customer> customers, SmsGateway gateway, string orderId)
    {
        foreach (var c in customers)
            gateway.Transmit(new SmsMessage(c.Phone, $"Dear {c.Name}, order {orderId} is paid."));
    }
}
```

After: both channels sit behind `IMessageSender`. The adapter wraps the gateway, and the notifier has one loop.

```csharp
using System.Collections.Generic;

public record Customer(string Name, string Email, string Phone);
public record SmsMessage(string Number, string Text);

public interface IMessageSender
{
    void Send(string to, string subject, string body);
}

public class EmailSender : IMessageSender
{
    public List<string> Sent { get; } = new();
    public void Send(string to, string subject, string body) => Sent.Add($"{to}|{subject}|{body}");
}

// Third party: cannot be changed.
public sealed class SmsGateway
{
    public List<SmsMessage> Outbox { get; } = new();
    public void Transmit(SmsMessage message) => Outbox.Add(message);
}

public class SmsGatewayAdapter : IMessageSender
{
    private readonly SmsGateway _gateway;
    public SmsGatewayAdapter(SmsGateway gateway) => _gateway = gateway;

    // SMS has no subject; the address is the phone number.
    public void Send(string to, string subject, string body) =>
        _gateway.Transmit(new SmsMessage(to, body));
}

public class ReceiptNotifier
{
    public void Notify(IEnumerable<Customer> customers, IMessageSender sender, bool useEmail, string orderId)
    {
        foreach (var c in customers)
            sender.Send(useEmail ? c.Email : c.Phone, "Receipt", $"Dear {c.Name}, order {orderId} is paid.");
    }
}
```

The `useEmail` flag shows what is still different: how to get the address. If that bothers you, give the interface an address-selecting member, or let the caller pass the address list. That is a separate step.

## C# notes
- Prefer composition (a field holding the adaptee, as above) over inheriting from the third-party class, which may be `sealed` and ties you to its API.
- Keep the adapter's constructor strict: validate the adaptee is not null, and put the translation (names, units, error handling) in the adapter, not the client.
- If the interface is meant to be implemented by many classes you own, an interface is right. If you only need a function shape, `Action<...>` or `Func<...>` can replace a one-method interface.
- Register adapter and interface in your DI container if you use one, so clients receive `IMessageSender` and never see the adaptee.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The same inputs produce the same outbound messages through both channels as before (compare `Sent` and `Outbox`), and no client code still names the adaptee type.
