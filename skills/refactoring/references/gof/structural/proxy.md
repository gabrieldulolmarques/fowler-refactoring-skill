# Proxy

Gamma et al. (1995), ch. 4, p. 207. Also known as: Surrogate. Category: object structural.

## Intent
Put a stand-in with the same interface in front of another object, to control access to it: delay its creation, check permissions, reach it across a boundary, or do bookkeeping on each use.

## When it pays off
- A **virtual proxy** delays an expensive creation until the first real use. A **protection proxy** checks that the caller may do the operation. A **remote proxy** represents an object that lives elsewhere (a generated HTTP or RPC client is one). A **smart reference** adds work on access: counting, locking, loading on first touch, logging.
- Callers keep using the subject's interface and do not know a proxy is there.
- Copy-on-write is another use: copies share one subject until someone changes it.
- Liability: one more layer, and sometimes a hidden cost or failure (a network call that looks like a local call).
- Skip it when callers can create the object lazily themselves with `Lazy<T>`, or when a simple check in one place is enough.

## Participants in C#
- **Subject** (`IAssistantTool`): the interface shared by the real object and the proxy.
- **RealSubject** (`SearchTool`): the real object, possibly expensive to create.
- **Proxy** (`AuthorizedToolProxy`, `LazyToolProxy`): implements the subject interface, holds a reference or the means to get the real subject (a factory delegate), and decides whether and when to forward each call.

## Example (C#)
An AI chat assistant calls tools. A search tool is costly to initialize, so a virtual proxy creates it on first use. Another tool is restricted, so a protection proxy checks the caller's scopes before forwarding.

```csharp
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

public interface IAssistantTool
{
    string Name { get; }
    Task<string> RunAsync(string input);
}

public class SearchTool : IAssistantTool
{
    public string Name => "search";

    public SearchTool()
    {
        Console.WriteLine("loading search index...");
    }

    public Task<string> RunAsync(string input) => Task.FromResult($"3 results for '{input}'");
}

public class FileDeleteTool : IAssistantTool
{
    public string Name => "delete_file";

    public Task<string> RunAsync(string input) => Task.FromResult($"deleted {input}");
}

// Virtual proxy: creates the real tool on first use.
public class LazyToolProxy : IAssistantTool
{
    private readonly Lazy<IAssistantTool> _real;

    public LazyToolProxy(string name, Func<IAssistantTool> factory)
    {
        Name = name;
        _real = new Lazy<IAssistantTool>(factory);
    }

    public string Name { get; }

    public Task<string> RunAsync(string input) => _real.Value.RunAsync(input);
}

// Protection proxy: checks the caller's scopes before forwarding.
public class AuthorizedToolProxy : IAssistantTool
{
    private readonly IAssistantTool _real;
    private readonly IReadOnlyCollection<string> _scopes;
    private readonly string _requiredScope;

    public AuthorizedToolProxy(IAssistantTool real, IReadOnlyCollection<string> callerScopes, string requiredScope)
    {
        _real = real;
        _scopes = callerScopes;
        _requiredScope = requiredScope;
    }

    public string Name => _real.Name;

    public Task<string> RunAsync(string input)
    {
        if (!((ICollection<string>)_scopes).Contains(_requiredScope))
            return Task.FromResult($"refused: {Name} needs scope '{_requiredScope}'");
        return _real.RunAsync(input);
    }
}

public static class Program
{
    public static async Task Main()
    {
        var scopes = new List<string> { "read" };
        var tools = new List<IAssistantTool>
        {
            new LazyToolProxy("search", () => new SearchTool()),
            new AuthorizedToolProxy(new FileDeleteTool(), scopes, "write")
        };

        Console.WriteLine("assistant ready");
        foreach (IAssistantTool tool in tools)
            Console.WriteLine(await tool.RunAsync("quarterly report"));
    }
}
```

## Variations
- **Proxy that knows only the interface**: when the proxy reaches the subject through the interface alone, one proxy class serves all subjects (the protection proxy above). A virtual proxy needs to construct the subject, so it takes a factory delegate or a concrete type.
- **Reference before creation**: until the subject exists, the proxy keeps an indirect reference to it (an id, a file name, a URL) and may cache cheap facts (a size) to answer without loading.
- **Automatic forwarding**: in C# you can build proxies without writing every forwarding method by using a runtime proxy generator (`DispatchProxy` or a library), where one handler sees every call. That suits cross-cutting checks, at the cost of speed and weaker compile-time checking.
- **Copy-on-write**: copies share one subject. The proxy copies it only at the first write.

## Risks and C# alternatives
- `Lazy<T>` covers most virtual proxies without a new class. Use a proxy class only when callers need the subject's interface and must not know about laziness.
- Make remote proxies honest: the interface should be asynchronous (`Task`) and callers should expect failures and timeouts. A remote call dressed as a local one hides cost.
- A protection proxy is not the only line of defense. Enforce the same checks on the server side for anything a client can bypass.
- `DispatchProxy` and similar tools use reflection, so they are slower and are not friendly to ahead-of-time compilation or trimming.
- Do not let the proxy accumulate unrelated duties. Several responsibilities (access control, caching, logging) are cleaner as separate wrappers; see the decorator.
- Compare identities carefully: the proxy and the subject are different objects.

## Related patterns
- [adapter.md](adapter.md): gives the adapted object a different interface. A proxy keeps the same one (a protection proxy may refuse some operations, so it can be effectively a subset).
- [decorator.md](decorator.md): can be built the same way, but a decorator adds responsibilities and stacks, while a proxy controls access to its subject. A protection proxy may look just like a decorator. A remote or virtual proxy may hold only an indirect reference at first.

## Verification
- Client code uses only the subject interface and does not change when a proxy is put in or taken out.
- With a virtual proxy, creating the proxy does no expensive work, and the first call triggers creation exactly once (also under concurrent calls).
- Tests show that a refused call never reaches the real subject.
- Failure and timeout paths of a remote proxy are tested, not just the successful call.
