# Move Embellishment to Decorator

Kerievsky (2004), ch. 7, p. 144. Pattern: Decorator. Direction: to, towards.

## When to use
Smells: Conditional Complexity, Primitive Obsession.

- A class has accumulated an embellishment around its core job (extra fields, methods and flags used only some of the time, such as auditing or retrying) and conditionals decide whether to apply it.
- Each embellishment goes into its own class that wraps an object of the same type. Clients stack them at runtime only where they are needed.
- Do not use it when the class has dozens of public methods: a Decorator must implement every public method of the type it wraps. Consider [replace-conditional-logic-with-strategy.md](replace-conditional-logic-with-strategy.md) instead.
- Against Strategy: a Decorator wraps an object and shares its interface, so one decorator can wrap many classes but cannot be shared between objects; a Strategy lives inside an object and may have any interface, but the host class must know about it.
- Liabilities: the decorated object has a different identity (type checks and casts on the original fail), several decorators can interfere with each other depending on their order, and debugging has to step through the wrappers. If the embellishment only guards access, the structure is a Protection Proxy.

## Mechanics
Identify the embellished class. First check that the set of public methods a decorator would need to implement is small. If not, shrink it or choose another refactoring.

1. Find or create the enclosure type: an interface (or class) that declares every public method clients use on the embellished class. Prefer an interface, since a base class with state would pass that state on to the decorators. Create it with Unify Interfaces ([unify-interfaces.md](../utilities/unify-interfaces.md)) and/or Extract Interface (1st ed. only; no link). (Adaptation, not in the book: make the embellished class implement it and change clients to depend on it.)
2. Remove the conditional that applies the embellishment with [replace-conditional-with-polymorphism.md](../../fowler/conditional-logic/replace-conditional-with-polymorphism.md), which usually starts with [replace-type-code-with-subclasses.md](../../fowler/inheritance/replace-type-code-with-subclasses.md). If a creation method is needed to hide the type code, make it return the enclosure type. When you remove the type code field from the superclass, the type code accessors need not be declared abstract, although Fowler's mechanics say they must. If the embellishment must run before and after the core logic, form a template method first ([form-template-method.md](../generalization/form-template-method.md)). Compile and test.
3. Each subclass from step 2 now holds one embellishment. Turn it into a delegating class with Replace Superclass with Delegate ([replace-superclass-with-delegate.md](../../fowler/inheritance/replace-superclass-with-delegate.md)). The delegating class implements the enclosure type, its delegate field has the enclosure type, and you decide whether the embellishment runs before or after each delegated call. If the template method needs non-public members of the embellished class, make them public and unify the interface again. If a delegated method can return an undecorated instance, decorate it before handing it out. Compile and test.
4. The delegating class creates its own delegate in the constructor. Apply Extract Parameter ([extract-parameter.md](../utilities/extract-parameter.md)) so the caller passes the object to wrap, then remove constructor parameters that became useless with [change-function-declaration.md](../../fowler/first-set/change-function-declaration.md). Compile and test.

## Example
Before: one class both moves money and optionally sends status notifications, deciding with a flag in every method.

```csharp
using System;

public class PaymentResult
{
    public bool Approved { get; }
    public string Reference { get; }

    public PaymentResult(bool approved, string reference)
    {
        Approved = approved;
        Reference = reference;
    }
}

public class PaymentGateway
{
    private readonly bool _notify;
    private readonly Action<string>? _notifier;

    public PaymentGateway(bool notify, Action<string>? notifier)
    {
        _notify = notify;
        _notifier = notifier;
    }

    public PaymentResult Authorize(string account, decimal amount)
    {
        var result = new PaymentResult(amount > 0, $"auth-{account}-{amount}");
        if (_notify) _notifier!($"authorize {amount} on {account}: approved={result.Approved}");
        return result;
    }

    public PaymentResult Refund(string reference, decimal amount)
    {
        var result = new PaymentResult(amount > 0, reference);
        if (_notify) _notifier!($"refund {amount} of {reference}: approved={result.Approved}");
        return result;
    }
}
```

After: the core class knows nothing about notifications, and `NotifyingPaymentGateway` wraps any `IPaymentGateway`. Clients that want notifications wrap the gateway when they create it: `IPaymentGateway g = new NotifyingPaymentGateway(new PaymentGateway(), messages.Add);`. A second decorator (retry, rate limiting) wraps the first the same way, and the order of wrapping then matters.

```csharp
using System;

public interface IPaymentGateway
{
    PaymentResult Authorize(string account, decimal amount);
    PaymentResult Refund(string reference, decimal amount);
}

public class PaymentGateway : IPaymentGateway
{
    public PaymentResult Authorize(string account, decimal amount) =>
        new(amount > 0, $"auth-{account}-{amount}");

    public PaymentResult Refund(string reference, decimal amount) =>
        new(amount > 0, reference);
}

public class NotifyingPaymentGateway : IPaymentGateway
{
    private readonly IPaymentGateway _inner;
    private readonly Action<string> _notifier;

    public NotifyingPaymentGateway(IPaymentGateway inner, Action<string> notifier)
    {
        _inner = inner;
        _notifier = notifier;
    }

    public PaymentResult Authorize(string account, decimal amount)
    {
        var result = _inner.Authorize(account, amount);
        _notifier($"authorize {amount} on {account}: approved={result.Approved}");
        return result;
    }

    public PaymentResult Refund(string reference, decimal amount)
    {
        var result = _inner.Refund(reference, amount);
        _notifier($"refund {amount} of {reference}: approved={result.Approved}");
        return result;
    }
}
```

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The undecorated class has a test with no notifications at all, and the decorator has a test with a fake inner gateway that checks the calls are forwarded unchanged.
- Search for `is` / `as` / casts to the embellished class: those callers break once the object is wrapped.
