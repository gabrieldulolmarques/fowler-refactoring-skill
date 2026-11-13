# Move Embellishment to Decorator

Kerievsky (2004), ch. 7, p. 144. Direction: to, towards. Pattern: Decorator (GoF, p. 175).

## When to use
Smells: Conditional Complexity, Primitive Obsession.

- A class has accumulated an embellishment around its core job (extra fields, methods and flags used only some of the time, such as auditing or retrying) and conditionals decide whether to apply it.
- Each embellishment goes into its own class that wraps an object of the same type. Clients stack them at runtime only where they are needed.
- Do not use it when the class has dozens of public methods: a Decorator must implement every public method of the type it wraps. Consider [replace-conditional-logic-with-strategy.md](replace-conditional-logic-with-strategy.md) instead.
- Against Strategy: a Decorator wraps an object and shares its interface, so one decorator can wrap many classes but cannot be shared between objects; a Strategy lives inside an object and may have any interface, but the host class must know about it.
- Liabilities: the decorated object has a different identity (type checks and casts on the original fail), several decorators can interfere with each other depending on their order, and debugging has to step through the wrappers. If the embellishment only guards access, the structure is a Protection Proxy.

## Mechanics
Identify the embellished class. First check that the set of public methods a decorator would need to implement is small. If not, shrink it or choose another refactoring.

1. Find or create the enclosure type: an interface (or class) that declares every public method clients use on the embellished class. Prefer an interface, since a base class with state would pass that state on to the decorators. Create it with Unify Interfaces ([unify-interfaces.md](../utilities/unify-interfaces.md)) and/or Extract Interface (1st ed. only; no link). Make the embellished class implement it and change clients to depend on it.
2. Remove the conditional that applies the embellishment with [replace-conditional-with-polymorphism.md](../conditional-logic/replace-conditional-with-polymorphism.md), which usually starts with [replace-type-code-with-subclasses.md](../inheritance/replace-type-code-with-subclasses.md). If a creation method is needed to hide the type code, make it return the enclosure type. If the embellishment must run before and after the core logic, form a template method first ([form-template-method.md](../generalization/form-template-method.md)). Compile and test.
3. Each subclass from step 2 now holds one embellishment. Turn it into a delegating class with Replace Inheritance with Delegation ([replace-superclass-with-delegate.md](../inheritance/replace-superclass-with-delegate.md)). The delegating class implements the enclosure type, its delegate field has the enclosure type, and you decide whether the embellishment runs before or after each delegated call. If the template method needs non-public members of the embellished class, make them public and unify the interface again. If a delegated method can return an undecorated instance, decorate it before handing it out. Compile and test.
4. The delegating class creates its own delegate in the constructor. Apply Extract Parameter ([extract-parameter.md](../utilities/extract-parameter.md)) so the caller passes the object to wrap, then remove constructor parameters that became useless with [change-function-declaration.md](../first-set/change-function-declaration.md). Compile and test.

## Example
Before: one class both processes payments and optionally writes an audit trail, deciding with a flag in every method.

```csharp
using System.Collections.Generic;

public record PaymentResult(bool Approved, string Reference);

public class PaymentProcessor
{
    private readonly bool _audited;
    private readonly List<string> _audit;

    public PaymentProcessor(bool audited, List<string> audit)
    {
        _audited = audited;
        _audit = audit;
    }

    public PaymentResult Charge(string account, decimal amount)
    {
        if (_audited) _audit.Add($"charge {amount} to {account}");
        var result = new PaymentResult(amount > 0, $"ref-{account}-{amount}");
        if (_audited) _audit.Add($"charge approved={result.Approved}");
        return result;
    }

    public PaymentResult Refund(string reference, decimal amount)
    {
        if (_audited) _audit.Add($"refund {amount} of {reference}");
        var result = new PaymentResult(amount > 0, reference);
        if (_audited) _audit.Add($"refund approved={result.Approved}");
        return result;
    }
}
```

After: the core class knows nothing about auditing, and `AuditedPaymentProcessor` wraps any `IPaymentProcessor`. Clients that want an audit wrap the processor when they create it: `IPaymentProcessor p = new AuditedPaymentProcessor(new PaymentProcessor(), log);`. A second decorator (retry, rate limiting) wraps the first the same way, and the order of wrapping then matters.

```csharp
using System.Collections.Generic;

public record PaymentResult(bool Approved, string Reference);

public interface IPaymentProcessor
{
    PaymentResult Charge(string account, decimal amount);
    PaymentResult Refund(string reference, decimal amount);
}

public class PaymentProcessor : IPaymentProcessor
{
    public PaymentResult Charge(string account, decimal amount) =>
        new(amount > 0, $"ref-{account}-{amount}");

    public PaymentResult Refund(string reference, decimal amount) =>
        new(amount > 0, reference);
}

public class AuditedPaymentProcessor : IPaymentProcessor
{
    private readonly IPaymentProcessor _inner;
    private readonly List<string> _audit;

    public AuditedPaymentProcessor(IPaymentProcessor inner, List<string> audit)
    {
        _inner = inner;
        _audit = audit;
    }

    public PaymentResult Charge(string account, decimal amount)
    {
        _audit.Add($"charge {amount} to {account}");
        var result = _inner.Charge(account, amount);
        _audit.Add($"charge approved={result.Approved}");
        return result;
    }

    public PaymentResult Refund(string reference, decimal amount)
    {
        _audit.Add($"refund {amount} of {reference}");
        var result = _inner.Refund(reference, amount);
        _audit.Add($"refund approved={result.Approved}");
        return result;
    }
}
```

## C# notes
- If the interface grows later, every decorator must grow with it. Keep it small.
- With a DI container, register the decorated chain in one place so call sites do not pick the order.
- Do not test the decorated object with `is` or casts to the concrete class; depend on the interface.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The undecorated class has a test with no audit at all, and the decorator has a test with a fake inner processor that checks the calls are forwarded unchanged.
- Search for `is` / `as` / casts to the embellished class: those callers break once the object is wrapped.
