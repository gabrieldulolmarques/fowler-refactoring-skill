# Chain of Responsibility

Gamma et al. (1995), ch. 5, p. 223. Category: object behavioral.

## Intent
Let several objects have a chance to handle a request, so the sender does not need to know which one will. The receivers are linked, and the request travels along the links until one of them takes it.

## When it pays off
- More than one object can handle a request, and which one is only known at run time.
- You want to send a request without naming the receiver, or the set of possible receivers must be configurable.
- Benefit: sender and receivers are decoupled. Each handler keeps one reference (its successor) instead of knowing every candidate, and the chain can be reordered or extended at run time.
- Liability: nothing guarantees the request is handled. It can fall off the end of the chain, or the chain can be wired wrongly. Decide what an unhandled request means and make it visible.
- Not worth it when the receiver is known statically, or when every step must always run (that is a pipeline, not a chain: see Variations).

## Participants in C#
- **Handler** (`PaymentCheck`): abstract class (or interface) that declares the handling method and, optionally, keeps the successor link and the forwarding default.
- **ConcreteHandler** (`LimitCheck`, `FraudCheck`, `BalanceCheck`): decides whether the request is its business. If so it handles it, otherwise it calls the successor.
- **Client** (`Program` in the example): builds the chain and sends the request to the first handler.

## Example (C#)
An instant-payment request goes through screening steps. Each step either rejects the payment or passes it on; the last one approves it. The request is an object, so new data does not change the handler signature.

```csharp
using System;

public class PaymentRequest
{
    public PaymentRequest(string payerId, decimal amount, string country)
    {
        PayerId = payerId;
        Amount = amount;
        Country = country;
    }

    public string PayerId { get; }
    public decimal Amount { get; }
    public string Country { get; }
}

public class PaymentDecision
{
    public PaymentDecision(bool approved, string reason)
    {
        Approved = approved;
        Reason = reason;
    }

    public bool Approved { get; }
    public string Reason { get; }
}

public abstract class PaymentCheck
{
    private PaymentCheck? _next;

    // Returns the handler passed in, so calls can be chained when wiring.
    public PaymentCheck SetNext(PaymentCheck next)
    {
        _next = next;
        return next;
    }

    public virtual PaymentDecision Handle(PaymentRequest request) =>
        _next != null
            ? _next.Handle(request)
            : new PaymentDecision(false, "no check approved the payment");
}

public class LimitCheck : PaymentCheck
{
    private readonly decimal _maxAmount;

    public LimitCheck(decimal maxAmount) => _maxAmount = maxAmount;

    public override PaymentDecision Handle(PaymentRequest request) =>
        request.Amount > _maxAmount
            ? new PaymentDecision(false, "amount above the instant-payment limit")
            : base.Handle(request);
}

public class FraudCheck : PaymentCheck
{
    private readonly string[] _blockedCountries;

    public FraudCheck(params string[] blockedCountries) => _blockedCountries = blockedCountries;

    public override PaymentDecision Handle(PaymentRequest request) =>
        Array.IndexOf(_blockedCountries, request.Country) >= 0
            ? new PaymentDecision(false, "destination country is blocked")
            : base.Handle(request);
}

public class BalanceCheck : PaymentCheck
{
    private readonly Func<string, decimal> _balanceOf;

    public BalanceCheck(Func<string, decimal> balanceOf) => _balanceOf = balanceOf;

    public override PaymentDecision Handle(PaymentRequest request) =>
        _balanceOf(request.PayerId) >= request.Amount
            ? new PaymentDecision(true, "approved")
            : new PaymentDecision(false, "insufficient balance");
}

public static class Program
{
    public static void Main()
    {
        var first = new LimitCheck(5_000m);
        first.SetNext(new FraudCheck("XX", "YY"))
             .SetNext(new BalanceCheck(_ => 1_200m));

        Console.WriteLine(first.Handle(new PaymentRequest("p-1", 300m, "BR")).Reason);   // approved
        Console.WriteLine(first.Handle(new PaymentRequest("p-1", 9_000m, "BR")).Reason); // limit
        Console.WriteLine(first.Handle(new PaymentRequest("p-1", 300m, "XX")).Reason);   // blocked
    }
}
```

## Variations
- **Link location.** The handler base class can own the successor field (as above), or each concrete handler can define its own. When objects already form a hierarchy (a node and its parent), the existing parent reference can serve as the successor instead of a new link.
- **Request representation.** A fixed method per request type is simple and type-safe but closed. A code (string or enum) plus a switch is open but loses type safety on parameters. A request object, possibly with subclasses, bundles the parameters and is the usual middle ground. Handlers test the type with pattern matching and forward what they do not know.
- **Extending by inheritance.** A subclass can handle the requests it cares about and call `base.Handle` for the rest, so it extends the parent's handling instead of replacing it.
- **Handled versus passed through.** In the classic form the first handler that accepts ends the walk. A variant lets every handler act and always forward (a pipeline). Pick one and name it clearly, because callers reason about it differently.

## Risks and C# alternatives
- The silent end of the chain is the main bug source. Return a result that says "not handled" (as the default above does) or throw, instead of returning nothing.
- A cycle in the successor links loops forever. Build the chain in one place.
- For a short, fixed list, a loop over `IEnumerable<IPaymentCheck>` that returns the first non-null result is simpler than linked handlers, and the order is visible in one line. Use linked objects when handlers must decide dynamically whether to forward, or when the chain reuses an existing hierarchy.
- With dependency injection, register the handlers in order and build the chain in the composition root.
- Delegates work too: a list of `Func<PaymentRequest, PaymentDecision?>` replaces the class per step when handlers have no state of their own.

## Related patterns
- [Composite](../structural/composite.md): the parent of a component is often its successor, so the two are used together.
- [Command](command.md): a request object in a chain is often a command.
- [Decorator](../structural/decorator.md): structurally similar (a wrapped next object), but a decorator always adds behavior and forwards, while a handler may stop the request.

## Verification
- A request that each handler should take is taken by exactly that handler, with a test per handler.
- A request nobody handles produces an explicit "unhandled" outcome, not silence or an exception from a null successor.
- The sender holds a reference only to the first handler and compiles without referring to any concrete handler.
- Reordering or removing a handler changes behavior without editing the other handlers.
