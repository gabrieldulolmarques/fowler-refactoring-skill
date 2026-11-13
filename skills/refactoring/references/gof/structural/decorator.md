# Decorator

Gamma et al. (1995), ch. 4, p. 175. Also known as: Wrapper. Category: object structural.

## Intent
Add responsibilities to an individual object at runtime by wrapping it in another object that has the same interface. It is a flexible alternative to subclassing for each combination of features.

## When it pays off
- You want to add behavior (retries, caching, logging, compression) to some objects and not others, transparently to the callers, and possibly to remove it again.
- Subclassing would need one class per combination of features, or the class cannot be subclassed.
- Benefits: features are small, stackable pieces. You pay only for the ones you attach, and you can attach the same one twice.
- Liabilities: a decorated object is not the same object as the original (do not rely on identity or on type checks), and a stack of many look-alike small objects is harder to read and debug.
- Skip it when you need only one extra behavior in one place (a plain subclass or a direct call is enough), or when the component is so heavy and so full of members that every wrapper would have to forward dozens of them.

## Participants in C#
- **Component** (`IApiClient`): the interface shared by the real object and the wrappers. Keep it small.
- **ConcreteComponent** (`HttpApiClient`): the object that does the real work.
- **Decorator**: a base class that implements the component interface, holds another component and forwards calls to it. It is optional; with a single-method interface it is not worth having, and the example has none.
- **ConcreteDecorator** (`RetryingClient`, `CachingClient`, `LoggingClient`): implements the component interface, holds another component, forwards calls to it and adds behavior before or after.
- **Client** (code in `Main`): composes the stack and uses it through the component interface.

## Example (C#)
An HTTP API client gets retries and a response cache, and both are optional. The stack is built at one place.

```csharp
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

public interface IApiClient
{
    Task<string> GetAsync(string path);
}

public class HttpApiClient : IApiClient
{
    private int _calls;

    public Task<string> GetAsync(string path)
    {
        _calls++;
        if (_calls == 1)
            throw new InvalidOperationException("temporary failure");
        return Task.FromResult($"body of {path}");
    }
}

public class RetryingClient : IApiClient
{
    private readonly IApiClient _inner;
    private readonly int _maxAttempts;

    public RetryingClient(IApiClient inner, int maxAttempts)
    {
        _inner = inner;
        _maxAttempts = maxAttempts;
    }

    public async Task<string> GetAsync(string path)
    {
        for (int attempt = 1; ; attempt++)
        {
            try
            {
                return await _inner.GetAsync(path);
            }
            catch (InvalidOperationException) when (attempt < _maxAttempts)
            {
                await Task.Delay(10 * attempt);
            }
        }
    }
}

public class CachingClient : IApiClient
{
    private readonly IApiClient _inner;
    private readonly Dictionary<string, string> _cache = new();

    public CachingClient(IApiClient inner) => _inner = inner;

    public async Task<string> GetAsync(string path)
    {
        if (_cache.TryGetValue(path, out string? hit))
            return hit;
        string body = await _inner.GetAsync(path);
        _cache[path] = body;
        return body;
    }
}

public class LoggingClient : IApiClient
{
    private readonly IApiClient _inner;

    public LoggingClient(IApiClient inner) => _inner = inner;

    public async Task<string> GetAsync(string path)
    {
        Console.WriteLine($"GET {path}");
        string body = await _inner.GetAsync(path);
        Console.WriteLine($"GET {path} -> {body.Length} chars");
        return body;
    }
}

public static class Program
{
    public static async Task Main()
    {
        IApiClient client = new LoggingClient(new CachingClient(new RetryingClient(new HttpApiClient(), 3)));
        await client.GetAsync("/orders/7");
        await client.GetAsync("/orders/7"); // served from the cache
    }
}
```

## Variations
- **Order matters**: in the example the cache wraps the retries, so a cached hit never retries. Swapping them changes behavior. Document the intended order where the stack is built.
- **Single decorator without a base class**: with one responsibility to add, skip the abstract decorator and write the wrapper directly, as above.
- **Decorators with extra members**: a decorator may add an operation of its own (a method to clear the cache). Callers that use it must hold the concrete decorator, and then the transparency is lost for them.
- **Light component**: keep the shared interface to behavior, not data. A heavy component makes every wrapper expensive. When the component is heavy, give it a replaceable helper object (a strategy) for the part that varies instead.
- **Strategy instead of wrapping**: the component itself holds a replaceable behavior object. This changes the object's insides and lets the strategy have its own narrow interface, but the component must know about the extension point.

## Risks and C# alternatives
- For HTTP specifically, .NET already has this pattern: `DelegatingHandler` stacked on `HttpClient`. Use it instead of writing a new decorator chain when you use `HttpClient`.
- A cross-cutting decorator on a large interface means writing every member by hand. Source generators, a dynamic proxy library or middleware pipelines (delegates of the form `Func<Request, Func<Request, Task>, Task>`) reduce that repetition.
- In a DI container, register decorators by wrapping the registration of the inner service, so that no consumer builds the stack itself.
- Dispose chains correctly: if the inner object is `IDisposable`, the decorator that owns it must dispose it (or leave that to the container, but only one place should do it).
- Caching state inside a decorator needs a bound on size and a lifetime. The dictionary above grows forever and is not thread-safe, which is fine only for an illustration.

## Related patterns
- [adapter.md](adapter.md): changes the interface; a decorator keeps it and adds responsibilities.
- [composite.md](composite.md): same recursive shape, different purpose. A decorator can be seen as a composite with one child that adds behavior rather than aggregating. They are often used together.
- [strategy.md](../behavioral/strategy.md): changes the object's insides instead of wrapping its skin. Prefer it when the component is heavy.
- [proxy.md](proxy.md): similar in implementation, but a proxy controls access to its subject, while a decorator adds responsibilities and can be stacked.

## Verification
- Each decorator has one reason to exist and can be removed from the stack without breaking the others.
- Callers depend only on the component interface and never on a decorator type.
- A test per decorator uses a fake inner component. One test checks the combined order (for example that a cache hit makes no inner call).
- Disposal and exceptions pass through correctly: an exception from the inner call is either handled on purpose or propagates unchanged.
