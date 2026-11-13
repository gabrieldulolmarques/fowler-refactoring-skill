# Limit Instantiation with Singleton

Kerievsky (2004), ch. 9, p. 296. Pattern: Singleton. Direction: to.

## When to use
Smells: —. The book's motive is performance, not a smell.

- WARNING: done without profiling evidence, this is premature optimization. Using a Singleton out of habit, because it "makes code more efficient", is what the book calls Singletonitis, and the cure is [inline-singleton.md](../creation/inline-singleton.md). Optimized code is also harder to refactor than code that has not been optimized yet.
- Do it only when all three hold: users complain about performance, a profiler shows that creating the same objects over and over is a real cost, and the objects have no state or only state that can be shared.
- The book's case is a State object created on every transition. After profiling, making each stateless State a Singleton improved memory use, which was measured again after the change.
- Liabilities: the single instance can be reached from anywhere, which often points to a design flaw, and it does not help when the object holds state that cannot be shared.
- Beyond the book: if the measurement afterwards shows no gain, undo it. Ordinary objects are preferable to Singletons.

## Mechanics
These assume one constructor. Precondition: the class has no state, or only state that can be shared.

1. Pick a class that is instantiated many times. Apply [replace-constructors-with-creation-methods.md](../creation/replace-constructors-with-creation-methods.md) even though there is only one constructor. The creation method returns the class itself (or its base type). Compile and test.
2. Add a private static field of that type. Initialize it with an instance if you can. If construction needs arguments that only a client has, declare it without initializing. Compile.
3. Make the creation method return the field. When it has to be created lazily, do that inside the creation method from the arguments received. Compile and test.

## Example
Before: every feature flag creates its own rollout rule, which holds no state.

```csharp
public abstract class RolloutRule
{
    public abstract bool Includes(int userBucket);
}

public class AllUsersRollout : RolloutRule
{
    public override bool Includes(int userBucket) => true;
}

public class FeatureFlag
{
    public RolloutRule Rule { get; private set; } = new AllUsersRollout();
}
```

After: a creation method hands out one shared instance, and the constructor is private so nobody can bypass it.

```csharp
public class AllUsersRollout : RolloutRule
{
    private static readonly RolloutRule Instance = new AllUsersRollout();

    private AllUsersRollout() { }

    public static RolloutRule Create() => Instance;

    public override bool Includes(int userBucket) => true;
}

public class FeatureFlag
{
    public RolloutRule Rule { get; private set; } = AllUsersRollout.Create();
}
```

## C# notes
- A `static readonly` field initializer is thread-safe and lazy enough for most cases: the CLR runs it once. When construction is expensive or needs a later trigger, use `Lazy<T>`: `private static readonly Lazy<FlagSchema> Instance = new(() => new FlagSchema());`.
- In an application that already uses a dependency injection container, a singleton lifetime registration (`AddSingleton`) usually does this job without a static field and without global access, and the class stays a normal class that tests can construct. Prefer it where a container exists.
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Callers receive the same instance every time (`ReferenceEquals(a, b)`), and a profile or measurement taken before and after shows a real gain (measuring again is not a step of the book's mechanics; keep the change only if it paid off).
