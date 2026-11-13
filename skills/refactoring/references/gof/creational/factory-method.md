# Factory Method

Gamma et al. (1995), ch. 3, p. 107. Also known as: Virtual Constructor. Category: class creational.

## Intent
Give a class an overridable method that creates its product, so each subclass picks the concrete class and the base class never names it.

## When it pays off
- A base class knows when an object is needed but not which concrete class to create.
- The creating class is meant to leave the choice of product to its subclasses.
- A class hands work to one of several helper subclasses, and you want the knowledge of which helper applies kept in one place.
- It gives subclasses a hook: a method with a sensible default that a subclass can override to supply an extended version.
- Code depends only on the product interface, so new concrete products need no change to the base class.
- Liability: you may have to create a subclass of the creator only to change the product, which adds a point of evolution.
- Not worth it when the created class never changes. Use `new`, or a delegate if the choice is just a parameter.

## Participants in C#
- **Product** (`INotification`): interface of what the factory method returns.
- **ConcreteProduct** (`EmailNotification`, `PushNotification`): implementations.
- **Creator** (`NotificationService`): abstract (or concrete) class that declares the factory method (`CreateNotification`) and uses it inside its own logic. It may provide a default product.
- **ConcreteCreator** (`EmailNotificationService`, `PushNotificationService`): overrides the factory method to return a specific product.

## Example (C#)
A notification service sends an "order shipped" message. The flow is the same for every channel; only the channel object differs, so the base class leaves its creation to subclasses.

```csharp
using System;

public interface INotification
{
    void Send(string recipient, string text);
}

public class EmailNotification : INotification
{
    public void Send(string recipient, string text) =>
        Console.WriteLine($"[email to {recipient}] {text}");
}

public class PushNotification : INotification
{
    public void Send(string recipient, string text) =>
        Console.WriteLine($"[push to device {recipient}] {text}");
}

public abstract class NotificationService
{
    // the factory method
    protected abstract INotification CreateNotification();

    public void NotifyOrderShipped(string recipient, string orderId)
    {
        INotification notification = CreateNotification();
        notification.Send(recipient, $"Your order {orderId} has shipped.");
    }
}

public class EmailNotificationService : NotificationService
{
    protected override INotification CreateNotification() => new EmailNotification();
}

public class PushNotificationService : NotificationService
{
    protected override INotification CreateNotification() => new PushNotification();
}

public static class Program
{
    public static void Main()
    {
        NotificationService service = new PushNotificationService();
        service.NotifyOrderShipped("device-42", "A-1001");
    }
}
```

The parameterized form uses one creation method with a key, so no subclass is needed per product. The set of products is fixed in one switch, and an unknown key fails fast.

```csharp
public static class NotificationFactory
{
    public static INotification Create(string channel) => channel switch
    {
        "email" => new EmailNotification(),
        "push" => new PushNotification(),
        _ => throw new ArgumentException("Unknown channel: " + channel, nameof(channel))
    };
}
```

## Variations
- **Abstract creator or default implementation.** With an abstract creator, subclasses must supply the product because no reasonable default exists. With a concrete creator, the factory method returns a default product and exists only so subclasses can change it.
- **Parameterized factory method.** One method creates several kinds, selected by a parameter (enum, string, type). A subclass can extend the set by handling its own keys and delegating the rest to the base method. All products come back as the common interface, so callers needing more must cast.
- **Generic creator.** In C# a `Creator<TProduct> where TProduct : INotification, new()` creates the product without a subclass per product. It covers the case where the only job is to pick the class.
- **Lazy creation.** Do not call a virtual factory method from the base constructor: the derived class is not initialized yet. Create the product on first use through a property instead (`Lazy<T>` fits).
- **Naming.** Name factory methods so they read as such (`Create...`, `Make...`).

## Risks and C# alternatives
- A `Func<INotification>` passed to the constructor replaces a subclass-per-product hierarchy, and is often all that is needed.
- With dependency injection, the container is the factory; inject `INotification` (or a keyed lookup of implementations) rather than writing creators.
- Calling a virtual method from a constructor is legal in C# but runs before the derived constructor body, so it can see uninitialized fields. Avoid it.
- A static `Create(kind)` switch is simpler than a creator hierarchy when no behavior varies besides the class; the cost is that the switch must change for each new kind.
- Keep factory methods `protected` when only the creator uses them, so clients are not tempted to call them.

## Related patterns
- [Abstract Factory](abstract-factory.md): usually implemented as a set of factory methods.
- [Template Method](../behavioral/template-method.md): factory methods are commonly called from template methods (`NotifyOrderShipped` above).
- [Prototype](prototype.md): avoids subclassing the creator, but the product then needs a clone operation and often an initialization step.

## Verification
- The creator's code mentions only the product interface, never a concrete product.
- A new product is added by writing one subclass (or one switch arm) without editing the creator's logic.
- No virtual factory method is called from a constructor.
- If the subclasses only differ in the class they create, check whether a delegate or generic would be simpler.
