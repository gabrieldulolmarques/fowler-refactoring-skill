# Inline Singleton

Kerievsky (2004), ch. 6, p. 114. Pattern: Singleton. Direction: away.

## When to use
Smells: Lazy Class.

- Code needs an object but does not need a global way to reach it. The book's name for the habit of making too many Singletons is Singletonitis, and its answer to "when is a Singleton unnecessary?" is: most of the time.
- Passing the object as a parameter is usually simpler than reading it from a global. A Singleton is also unnecessary when it exists for a small speed or memory gain, or when code deep in one layer reaches for a resource that does not belong in that layer.
- Global state hurts tests: each test that changes the shared instance must save and restore it. The book quotes one team that spent half an hour passing a shared table of exchange rates as an explicit parameter and ended with a cleaner design and stable tests.
- The book passes on a view it attributes to others: global data deserves suspicion until the need for it is shown. If a Singleton or a Registry (a well-known object used to find other objects) really is the right design, keep it.
- Benefits: collaborations become visible; no code is needed to protect a single instance. Cost: when the object has to travel through many layers, passing it is awkward.
- The opposite move is [limit-instantiation-with-singleton.md](../protection/limit-instantiation-with-singleton.md), for the rare case where one instance is a real need.

## Mechanics
These are the same as Inline Class ([inline-class.md](../../fowler/encapsulation/inline-class.md)). The *absorbing class* is the one that takes over the Singleton's job.
1. Declare the Singleton's public members on the absorbing class and make them delegate to the Singleton. Remove `static` from them unless the absorbing class is itself a Singleton.
2. Change every client reference to the Singleton to refer to the absorbing class. Compile and test.
3. Move the remaining members from the Singleton to the absorbing class, one at a time, with Move Function ([move-function.md](../../fowler/moving-features/move-function.md)) and Move Field ([move-field.md](../../fowler/moving-features/move-field.md)), until nothing is left. Drop `static` as in step 1. Compile and test after each.
4. Delete the Singleton.

When the absorbing class is a client or a collaborator that already holds the object, the end result is that the object is given to it (constructor or parameter) instead of being looked up.

## Example
Before: `EndpointRegistry` is a global that `ReportClient` reads. Tests that need a different base URL must change it and put it back.

```csharp
public class EndpointConfig { public virtual string BaseUrl => "https://api.example.test"; }

public static class EndpointRegistry
{
    public static EndpointConfig Config { get; set; } = new();
}

public class ReportClient
{
    public string UrlFor(string path) => EndpointRegistry.Config.BaseUrl + path;
}
```

After: `ReportClient` receives the `EndpointConfig` it uses. `EndpointRegistry` is deleted. Callers pass the config in, and a test passes its own.

```csharp
public class EndpointConfig { public virtual string BaseUrl => "https://api.example.test"; }

public class ReportClient
{
    private readonly EndpointConfig _config;
    public ReportClient(EndpointConfig config) { _config = config; }

    public string UrlFor(string path) => _config.BaseUrl + path;
}
```

In steps, `ReportClient` first gets a `Config` property that returns `EndpointRegistry.Config`, callers switch to it, then the field moves in and `EndpointRegistry` is removed.

## C# notes
- A `static class` or a class with a static `Instance` property are both Singletons for this purpose. The refactoring is the same.
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- A search for the Singleton's name finds nothing, and no test needs to reset shared state.
- Every class that used the global now shows the object in its constructor or method signature.
