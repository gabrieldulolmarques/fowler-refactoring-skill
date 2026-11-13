# Hide Delegate

Fowler (2018), ch. 7, p. 189. Formerly / aka: —. Inverse: Remove Middle Man
([remove-middle-man.md](remove-middle-man.md)).

## When to use
Smells: Message Chains, Insider Trading.

- Client code reaches through a server to an object it holds (`order.Customer.Region.Manager`),
  so the client knows how the server is built and which object owns the data.
- If the delegate's interface changes, every client of the server that touches the delegate has
  to change too. A forwarding method on the server confines that change to one place.
- Do not keep adding forwarders for every delegate member out of habit. When the server turns
  into a list of pass-through methods, the hiding costs more than it gives: see Remove Middle
  Man. How much to hide is a judgment you can revise later.

## Mechanics
1. For each delegate member a client uses, add a simple forwarding method on the server.
2. Compile and test.
3. Change one client at a time to call the server instead of going through the delegate.
   Compile and test after each client.
4. Once the last client has stopped going through the server to the delegate, take away the
   public getter that exposes it (delete it or lower its visibility).
5. Compile and test.

## Example
Before: the client navigates through the subscription to its plan's monthly price.

```csharp
public class Plan
{
    public decimal MonthlyPrice { get; set; }
}

public class Subscription
{
    public Plan Plan { get; set; } = null!;
}

public static class Client
{
    public static decimal Price(Subscription subscription)
    {
        decimal price = subscription.Plan.MonthlyPrice;
        return price;
    }
}
```

After: `Subscription` hides `Plan`.

```csharp
public class Subscription
{
    private Plan _plan = null!;

    public Plan Plan { get => _plan; set => _plan = value; } // removed in step 4
    public decimal MonthlyPrice => _plan.MonthlyPrice;
}

public static class Client
{
    public static decimal Price(Subscription subscription)
    {
        decimal price = subscription.MonthlyPrice;
        return price;
    }
}
```

Once every client uses `MonthlyPrice`, delete the public `Plan` accessor (or make it
private), so the delegate can no longer be reached from outside.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- No client still references the delegate type through the server.
