# Limit Instantiation with Singleton

Kerievsky (2004), ch. 9, p. 296. Pattern: Singleton. Direction: to.

## When to use
Smells: —. The book's motive is performance, not a smell.

- WARNING: this is usually premature optimization. Using a Singleton out of habit, because it "makes code more efficient", is what the book calls Singletonitis, and the cure is [inline-singleton.md](../creation/inline-singleton.md). Optimized code is also harder to refactor than code that has not been optimized yet.
- Do it only when all three hold: users complain about performance, a profiler shows that creating the same objects over and over is a real cost, and the objects have no state or only state that can be shared.
- The book's case is a State object created on every transition. After profiling, making each stateless State a Singleton improved memory use, which was measured again after the change.
- Liabilities: the single instance can be reached from anywhere, which often points to a design flaw, and it does not help when the object holds state that cannot be shared.
- If the measurement afterwards shows no gain, undo it. Ordinary objects are preferable to Singletons.

## Mechanics
These assume one constructor.

1. Pick a class that is instantiated many times. Apply [replace-constructors-with-creation-methods.md](../creation/replace-constructors-with-creation-methods.md) even though there is only one constructor. The creation method returns the class itself (or its base type). Compile and test.
2. Add a private static field of that type. Initialize it with an instance if you can. If construction needs arguments that only a client has, declare it without initializing. Compile.
3. Make the creation method return the field. When it has to be created lazily, do that inside the creation method from the arguments received. Compile and test.
4. Measure again. Keep the change only if it paid off.

## Example
Before: every order creates its own shipping policy, which holds no state.

```csharp
public abstract class ShippingPolicy
{
    public abstract decimal Cost(decimal weightKg);
}

public class StandardShipping : ShippingPolicy
{
    public override decimal Cost(decimal weightKg) => 4m + weightKg * 0.5m;
}

public class Order
{
    public ShippingPolicy Shipping { get; private set; } = new StandardShipping();
}
```

After: a creation method hands out one shared instance, and the constructor is private so nobody can bypass it.

```csharp
public class StandardShipping : ShippingPolicy
{
    private static readonly ShippingPolicy Instance = new StandardShipping();

    private StandardShipping() { }

    public static ShippingPolicy Create() => Instance;

    public override decimal Cost(decimal weightKg) => 4m + weightKg * 0.5m;
}

public class Order
{
    public ShippingPolicy Shipping { get; private set; } = StandardShipping.Create();
}
```

## C# notes
- A `static readonly` field initializer is thread-safe and lazy enough for most cases: the CLR runs it once. When construction is expensive or needs a later trigger, use `Lazy<T>`: `private static readonly Lazy<TaxTable> Instance = new(() => new TaxTable());`.
- In an application that already uses a dependency injection container, a singleton lifetime registration (`AddSingleton`) usually does this job without a static field and without global access, and the class stays a normal class that tests can construct. Prefer it where a container exists.
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Callers receive the same instance every time (`ReferenceEquals(a, b)`), and a profile or measurement taken before and after shows a real gain.
