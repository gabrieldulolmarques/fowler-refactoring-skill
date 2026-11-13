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
- **Handler** (`PaymentRoute`): abstract class (or interface) that declares the handling method and, optionally, keeps the successor link and the forwarding default.
- **ConcreteHandler** (`BrlInstantRoute`, `EurInstantRoute`, `ManualReviewRoute`): decides whether the request is its business. If so it handles it, otherwise it calls the successor.
- **Client** (`Program` in the example): builds the chain and sends the request to the first handler.

## Example (C#)
An instant-payment request is routed to the rail that serves its currency. Exactly one handler takes each request: the first route that supports the currency, or the manual-review route at the end of the chain as the fallback. The request is an object, so new data does not change the handler signature.

```csharp
using System;

public class PaymentRequest
{
    public PaymentRequest(string payerId, decimal amount, string currency)
    {
        PayerId = payerId;
        Amount = amount;
        Currency = currency;
    }

    public string PayerId { get; }
    public decimal Amount { get; }
    public string Currency { get; }
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

public abstract class PaymentRoute
{
    private PaymentRoute? _next;

    // Returns the handler passed in, so calls can be chained when wiring.
    public PaymentRoute SetNext(PaymentRoute next)
    {
        _next = next;
        return next;
    }

    public virtual PaymentDecision Handle(PaymentRequest request)
    {
        if (CanHandle(request))
        {
            return Process(request);
        }

        return _next != null
            ? _next.Handle(request)
            : new PaymentDecision(false, "no route accepts the payment");
    }

    protected abstract bool CanHandle(PaymentRequest request);

    protected abstract PaymentDecision Process(PaymentRequest request);
}

public class BrlInstantRoute : PaymentRoute
{
    protected override bool CanHandle(PaymentRequest request) => request.Currency == "BRL";

    protected override PaymentDecision Process(PaymentRequest request) =>
        new PaymentDecision(true, "sent through the domestic instant rail");
}

public class EurInstantRoute : PaymentRoute
{
    private readonly decimal _maxAmount;

    public EurInstantRoute(decimal maxAmount) => _maxAmount = maxAmount;

    protected override bool CanHandle(PaymentRequest request) =>
        request.Currency == "EUR" && request.Amount <= _maxAmount;

    protected override PaymentDecision Process(PaymentRequest request) =>
        new PaymentDecision(true, "sent through the euro instant rail");
}

// Fallback: accepts whatever the earlier routes did not.
public class ManualReviewRoute : PaymentRoute
{
    protected override bool CanHandle(PaymentRequest request) => true;

    protected override PaymentDecision Process(PaymentRequest request) =>
        new PaymentDecision(false, "queued for manual review");
}

public static class Program
{
    public static void Main()
    {
        var first = new BrlInstantRoute();
        first.SetNext(new EurInstantRoute(100_000m))
             .SetNext(new ManualReviewRoute());

        Console.WriteLine(first.Handle(new PaymentRequest("p-1", 300m, "BRL")).Reason); // domestic instant rail
        Console.WriteLine(first.Handle(new PaymentRequest("p-1", 300m, "EUR")).Reason); // euro instant rail
        Console.WriteLine(first.Handle(new PaymentRequest("p-1", 300m, "JPY")).Reason); // manual review
    }
}
```

## Variations
- **Link location.** The handler base class can own the successor field (as above), or each concrete handler can define its own. When objects already form a hierarchy (a node and its parent), the existing parent reference can serve as the successor instead of a new link.
- **Request representation.** A fixed method per request type is simple and type-safe but closed. A code (string or enum) plus a switch is open but loses type safety on parameters. A request object, possibly with subclasses, bundles the parameters and is the usual middle ground. Handlers test the type with pattern matching and forward what they do not know.
- **Extending by inheritance.** A subclass can handle the requests it cares about and call `base.Handle` for the rest, so it extends the parent's handling instead of replacing it.
- **Handled versus passed through.** In the classic form the first handler that accepts ends the walk. A variant lets every handler act and always forward (a pipeline). Pick one and name it clearly, because callers reason about it differently.

## Risks and C# alternatives
- The silent end of the chain is the main bug source. Return a result that says "not handled" (as the default in `PaymentRoute` does) or throw, instead of returning nothing.
- A cycle in the successor links loops forever. Build the chain in one place.
- For a short, fixed list, a loop over `IEnumerable<PaymentRoute>` that returns the first non-null result is simpler than linked handlers, and the order is visible in one line. Use linked objects when handlers must decide dynamically whether to forward, or when the chain reuses an existing hierarchy.
- With dependency injection, register the handlers in order and build the chain in the composition root.
- Delegates work too: a list of `Func<PaymentRequest, PaymentDecision?>` replaces the class per step when handlers have no state of their own.

## Related patterns
- [Composite](../structural/composite.md): the parent of a component is often its successor, so the two are used together.
- [Command](command.md): a request object in a chain is often a command.

**Beyond the book:** [Decorator](../structural/decorator.md) looks similar structurally (a wrapped next object), but a decorator always adds behavior and forwards, while a handler may stop the request.

## Verification
- A request that each handler should take is taken by exactly that handler, with a test per handler.
- A request nobody handles produces an explicit "unhandled" outcome, not silence or an exception from a null successor.
- The sender holds a reference only to the first handler and compiles without referring to any concrete handler.
- Reordering or removing a handler changes behavior without editing the other handlers.
