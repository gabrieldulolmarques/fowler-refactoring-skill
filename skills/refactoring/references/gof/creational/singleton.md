# Singleton

Gamma et al. (1995), ch. 3, p. 127. Category: object creational.

## Intent
Guarantee that a class has exactly one instance and give a single, well-known point of access to it.

## When it pays off
- Exactly one instance must exist (one shared cache, one connection pool, one configuration source) and clients must reach it from a known place.
- The sole instance should be replaceable by a subclass or another implementation without changing client code.
- Benefits listed for the pattern: controlled access to the instance, no extra global names, the possibility to refine behavior by subclassing, and the freedom to later allow more than one instance.
- Warning: this is the most criticized of the creational patterns. Read "Risks and C# alternatives" below before using it. In most modern C# code, a singleton lifetime in a DI container is the better answer.
- Not worth it when the only need is "share one object": create it once and pass it to those who need it.

## Participants in C#
- **Singleton** (`FeatureFlags`): a sealed class with a private constructor, a private static field holding the instance, and a static `Instance` property that creates it on first use.

The interface (`IFeatureFlags`) is not part of the original pattern but is what makes the instance replaceable and testable.

## Example (C#)
A feature-flag store must exist once for the process. `Lazy<T>` gives lazy creation and thread safety without hand-written locking.

```csharp
using System;
using System.Collections.Generic;

public interface IFeatureFlags
{
    bool IsEnabled(string name);
}

public sealed class FeatureFlags : IFeatureFlags
{
    private static readonly Lazy<FeatureFlags> _instance = new(() => new FeatureFlags());

    public static FeatureFlags Instance => _instance.Value;

    private readonly HashSet<string> _enabled;

    private FeatureFlags()
    {
        // loaded once, on first access
        _enabled = new HashSet<string> { "new-checkout" };
    }

    public bool IsEnabled(string name) => _enabled.Contains(name);
}

public static class Program
{
    public static void Main()
    {
        Console.WriteLine(FeatureFlags.Instance.IsEnabled("new-checkout"));
    }
}
```

The preferred shape keeps the "one instance" decision at the composition point and passes the object in. The consumer has an ordinary public constructor and depends on the interface:

```csharp
public class CheckoutService
{
    private readonly IFeatureFlags _flags;

    public CheckoutService(IFeatureFlags flags) => _flags = flags;

    public string PickFlow() => _flags.IsEnabled("new-checkout") ? "new" : "legacy";
}

public class FixedFlags : IFeatureFlags
{
    private readonly bool _value;
    public FixedFlags(bool value) => _value = value;
    public bool IsEnabled(string name) => _value;
}

public static class Composition
{
    public static void Run()
    {
        // one shared instance, created once and handed down
        IFeatureFlags flags = FeatureFlags.Instance;
        var checkout = new CheckoutService(flags);

        // a test passes its own implementation
        var testCheckout = new CheckoutService(new FixedFlags(false));
        System.Console.WriteLine(checkout.PickFlow() + " " + testCheckout.PickFlow());

        // with a DI container the same intent is one line, for example:
        // services.AddSingleton<IFeatureFlags, FeatureFlags>();
    }
}
```

## Variations
- **Lazy creation.** Create the instance on first access. In C# use `Lazy<T>` (thread-safe by default) or a `static readonly` field, which the runtime initializes once and safely.
- **Eager creation.** `public static readonly FeatureFlags Instance = new FeatureFlags();` is the simplest thread-safe form, at the cost of creating the instance when the type is first touched.
- **Choosing a subclass.** The `Instance` code can pick the concrete class from configuration or an environment variable; this hard-wires the set of possible classes.
- **Registry of singletons.** `Instance` looks up an implementation by name in a registry that implementations register into. More flexible, and it moves the design towards a service locator.
- **Controlled number of instances.** Only the access operation has to change if you later need two, for example one per tenant.

## Risks and C# alternatives
- **Global state.** A static `Instance` is a global variable in disguise. Any code can read or change it, so behavior depends on who touched it before, and tests that run in one process leak state into each other.
- **Hidden dependencies.** A class that calls `FeatureFlags.Instance` inside its methods does not show the dependency in its constructor or signature. Readers and tools cannot see it, and replacing it means editing the class.
- **Testing.** You cannot substitute a fake without extra tricks (reset methods, reflection, test-only setters), and parallel tests interfere. Depending on an interface that is passed in removes all of this.
- **Prefer passing the instance.** Create the one object at startup and give it to the classes that need it, as a constructor parameter typed by an interface (second example above).
- **Prefer a container's singleton lifetime.** With dependency injection, `AddSingleton<IFeatureFlags, FeatureFlags>()` gives one shared instance for the application, with a public constructor, no static access, and the lifetime in one visible place.
- **`Lazy<T>` when the pattern is really needed.** When a static access point is unavoidable (a library entry point, code that cannot receive dependencies), use `Lazy<T>` or a `static readonly` field. Avoid hand-written double-checked locking.
- **Other hazards.** A singleton that holds mutable state needs its own synchronization. One that implements `IDisposable` needs a clear owner. One that depends on another singleton creates hidden initialization order. Static classes cannot implement interfaces or be injected.
- **Do not confuse "one instance needed" with "global access needed".** The first is a lifetime decision; the second is almost always avoidable.

## Related patterns
- [Abstract Factory](abstract-factory.md): a concrete factory is often a single shared instance, though it can simply be passed in.
- [Builder](builder.md): a builder can be shared, but is usually better as a transient object.
- [Prototype](prototype.md): a prototype manager is often a single shared instance.

## Verification
- The constructor is private (or the DI registration is the only way to get the instance) and creation is thread-safe.
- Consumers depend on an interface, and at least one test runs a consumer with a fake instead of the real singleton.
- Nothing mutable is exposed without synchronization, and no test depends on the order of other tests.
- Re-check that "exactly one instance" is a real requirement and not just convenience of access; if it is the latter, pass the object in.
