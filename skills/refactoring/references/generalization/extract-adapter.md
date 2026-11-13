# Extract Adapter

Kerievsky (2004), ch. 8, p. 258. Direction: to. Pattern: Adapter (GoF, p. 139).

## When to use
Smells: Solution Sprawl.

- One class adapts several versions of a component, library or API, so it carries version-specific fields, constructors, methods and conditionals. Comments like "delete when we drop version 1" stay forever, because nobody dares to remove code that something unknown may still use.
- One adapter per version, all behind a common interface, keeps each class responsible for one version. The class name can even carry the version. The program picks the right adapter from configuration or runtime information.
- Adapters also shield you from fast-changing APIs that you do not control.
- Do not do it before the multiple versions actually cause conditionals or maintenance trouble.
- An adapter can hide behavior the client needs, because the client only sees the adapter's interface. If so, widen the interface.
- An adapter wraps one object. If you need to wrap a whole subsystem behind a simpler view, that is a Facade, a different pattern.

## Mechanics
There are several routes. If a class uses conditionals to handle versions, you can usually get one adapter per version by applying Replace Conditional with Polymorphism ([replace-conditional-with-polymorphism.md](../conditional-logic/replace-conditional-with-polymorphism.md)) repeatedly. The steps below cover the other common case: an existing adapter class with version-specific fields and methods.

1. Identify the overburdened adapter, the class that adapts too many versions.
2. Create a new adapter for one version, by extracting a subclass (Extract Subclass is 1st ed. only; see [replace-type-code-with-subclasses.md](../inheritance/replace-type-code-with-subclasses.md)) or by Extract Class ([extract-class.md](../encapsulation/extract-class.md)). Move or copy to it every field and method used only by that version. You may have to widen the visibility of some members of the overburdened adapter, and initialize some fields through the new class's constructor, which changes the code that constructs it. Compile and test.
3. Repeat step 2 for each version until the overburdened adapter holds no version-specific code.
4. Remove the duplication among the new adapters with Pull Up Method ([pull-up-method.md](../inheritance/pull-up-method.md)) and Form Template Method ([form-template-method.md](form-template-method.md)). Compile and test.

## Example
Before: `ExchangeRates` adapts two versions of a rate service. It has two constructors, one nullable field per version, and a branch in the only method.

```csharp
using System;

// Old version of the external service.
public class LegacyRateService
{
    public decimal Rate(string pair) => pair == "USD/BRL" ? 5m : 1m;
}

// New version of the external service.
public record RateQuote(decimal Value, DateTime At);
public class RateServiceV2
{
    public RateQuote Quote(string from, string to) =>
        new(from == "USD" && to == "BRL" ? 5m : 1m, DateTime.UtcNow);
}

public class ExchangeRates
{
    private readonly LegacyRateService? _legacy;
    private readonly RateServiceV2? _v2;

    public ExchangeRates(LegacyRateService legacy) => _legacy = legacy;
    public ExchangeRates(RateServiceV2 v2) => _v2 = v2;

    public decimal Convert(decimal amount, string from, string to)
    {
        var rate = _legacy != null
            ? _legacy.Rate($"{from}/{to}")
            : _v2!.Quote(from, to).Value;
        return Math.Round(amount * rate, 2);
    }
}
```

After: one adapter per version, behind a common interface. The shared rounding stays in a base class (the Form Template Method step), and each adapter implements only how to get a rate.

```csharp
using System;

public class LegacyRateService
{
    public decimal Rate(string pair) => pair == "USD/BRL" ? 5m : 1m;
}

public record RateQuote(decimal Value, DateTime At);
public class RateServiceV2
{
    public RateQuote Quote(string from, string to) =>
        new(from == "USD" && to == "BRL" ? 5m : 1m, DateTime.UtcNow);
}

public interface IExchangeRates
{
    decimal Convert(decimal amount, string from, string to);
}

public abstract class ExchangeRates : IExchangeRates
{
    public decimal Convert(decimal amount, string from, string to) =>
        Math.Round(amount * RateFor(from, to), 2);

    protected abstract decimal RateFor(string from, string to);
}

public class LegacyExchangeRates : ExchangeRates
{
    private readonly LegacyRateService _service;
    public LegacyExchangeRates(LegacyRateService service) => _service = service;
    protected override decimal RateFor(string from, string to) => _service.Rate($"{from}/{to}");
}

public class V2ExchangeRates : ExchangeRates
{
    private readonly RateServiceV2 _service;
    public V2ExchangeRates(RateServiceV2 service) => _service = service;
    protected override decimal RateFor(string from, string to) => _service.Quote(from, to).Value;
}
```

Clients depend on `IExchangeRates`; startup code (or configuration) chooses `LegacyExchangeRates` or `V2ExchangeRates`. When version 1 is retired, delete one class and nothing else.

## C# notes
- Name each adapter after the version it serves, and keep the version-specific types out of the interface.
- Choose the adapter at the composition root (a factory or the DI container, using configuration), not inside the client.
- A common abstract base, as above, is one option; if the adapters share nothing, implement the interface directly and skip the base class.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Each adapter has a test against its own version (or a fake of it), and the old overburdened class has no version fields or branches left before you delete it.
