# Adapter

Gamma et al. (1995), ch. 4, p. 139. Also known as: Wrapper. Category: class, object structural.

## Intent
Make a class whose interface does not match what the client expects usable through the interface the client wants. The adapter translates calls, and the existing class stays unchanged.

## When it pays off
- You must reuse an existing class (a vendor SDK, a legacy service) whose members, units or data shapes differ from the interface your code is written against.
- You are writing a reusable component that should work with classes you cannot predict, and you would rather accept a narrow interface than force a base class on everyone.
- One object adapter can serve the adaptee and all its subclasses. It can also add behavior the adaptee lacks.
- Liability: the adapted object no longer is the adaptee type, so code that expects the original type cannot receive the adapter. A two-way adapter (implements both interfaces) solves that, at the cost of more code.
- Skip it when you own the adaptee and can simply change it, or when the translation is a single call site (a lambda or local function is enough).

## Participants in C#
- **Target** (`IPaymentProcessor`): the interface the client code is written against, a C# interface.
- **Client** (`CheckoutService`): uses only the target.
- **Adaptee** (`LegacyGatewayClient`): the existing class with an incompatible interface. It stays untouched.
- **Adapter** (`LegacyGatewayAdapter`): a class that implements the target and holds the adaptee in a field (object adapter). C# has no multiple class inheritance, so the class form is rare.

## Example (C#)
A checkout charges through `IPaymentProcessor`, with decimal amounts and a result object. A legacy gateway takes integer cents and returns a status string. The adapter converts both ways.

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

public interface IPaymentProcessor
{
    PaymentResult Charge(string customerId, decimal amount, string currency);
}

// Existing class we do not control.
public class LegacyGatewayClient
{
    public string SubmitTransaction(string account, long amountInCents, string currencyCode)
    {
        return amountInCents > 0 ? "OK:" + Guid.NewGuid().ToString("N") : "DECLINED:invalid-amount";
    }
}

public class LegacyGatewayAdapter : IPaymentProcessor
{
    private readonly LegacyGatewayClient _gateway;

    public LegacyGatewayAdapter(LegacyGatewayClient gateway) => _gateway = gateway;

    public PaymentResult Charge(string customerId, decimal amount, string currency)
    {
        long cents = (long)Math.Round(amount * 100m, MidpointRounding.AwayFromZero);
        string raw = _gateway.SubmitTransaction(customerId, cents, currency);
        int separator = raw.IndexOf(':');
        string status = raw.Substring(0, separator);
        string reference = raw.Substring(separator + 1);
        return new PaymentResult(status == "OK", reference);
    }
}

public class CheckoutService
{
    private readonly IPaymentProcessor _payments;

    public CheckoutService(IPaymentProcessor payments) => _payments = payments;

    public string Pay(string customerId, decimal total)
    {
        PaymentResult result = _payments.Charge(customerId, total, "USD");
        return result.Approved ? "paid " + result.Reference : "refused " + result.Reference;
    }
}

public static class Program
{
    public static void Main()
    {
        IPaymentProcessor processor = new LegacyGatewayAdapter(new LegacyGatewayClient());
        var checkout = new CheckoutService(processor);
        Console.WriteLine(checkout.Pay("cust-42", 19.99m));
    }
}
```

## Variations
- **Class adapter**: inherit from the adaptee and implement the target. It can override adaptee behavior, but it binds to one concrete adaptee and does not cover its subclasses. In C# it works when the adaptee is not sealed, and the adapter then implements the target interface on top of the base class.
- **Amount of adaptation**: from renaming methods, to converting data, to supplying whole operations the adaptee has no equivalent for (the adapter then implements them itself).
- **Pluggable adapter**: a reusable component finds the narrowest interface it needs from the thing it works on (for example "give me a node's label and its children") and gets it by one of three routes: abstract members that subclasses fill in, a delegate object that implements a small interface, or delegates (`Func<>`) passed to the constructor.
- **Two-way adapter**: implements both interfaces, so the adapted object can be used where either type is expected.

## Risks and C# alternatives
- When the adaptation is one or two members, pass `Func<>` delegates to the consumer instead of defining an interface and a class. This is the parameterized form of the pluggable adapter.
- Put the adapter at the boundary and register it in the dependency injection container as the implementation of the target interface. Do not let the adaptee type leak into the rest of the code, or the adapter protects nothing.
- Convert units, null conventions and error styles (status strings, error codes) inside the adapter, and turn them into the exceptions or result types the rest of the code uses.
- Do not let the adapter grow business rules. Once it decides things, it is a service with a translation inside.

## Related patterns
- [bridge.md](bridge.md): similar structure, but a bridge is planned up front so that an abstraction and its implementations vary independently. An adapter fixes a mismatch after the fact between existing parts.
- [decorator.md](decorator.md): keeps the interface and adds behavior, so it is transparent and can be stacked. An adapter changes the interface.
- [proxy.md](proxy.md): offers the same interface as its subject and controls access to it. An adapter offers a different one.
- [facade.md](facade.md): defines a new, simpler interface over a group of objects. An adapter reuses an interface that already exists on the client side.

## Verification
- Client code compiles against the target interface only and no longer mentions the adaptee type.
- A test feeds edge values (zero, rounding, a declined response) through the adapter and checks the converted result, not just the happy path.
- The adaptee class has no changes in its source.
- If you also inject a fake target in tests, the client tests need no adapter at all.
