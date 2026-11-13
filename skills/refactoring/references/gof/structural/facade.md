# Facade

Gamma et al. (1995), ch. 4, p. 185. Category: object structural.

## Intent
Give a set of classes in a subsystem one simple entry point, so that most clients do not have to know how the parts fit together.

## When it pays off
- A subsystem is made of many small classes that must be called in the right order, and most callers want a common case ("store this file") and not the details.
- Clients depend on many subsystem classes directly, and you want to cut those dependencies or define a clear entry point for each layer.
- Benefits: fewer objects for clients to know, weaker coupling to the subsystem (you can change its parts), and the lower-level classes stay public for the few clients that need them.
- Liabilities: the facade can grow into a god class that holds business rules, and if it hides everything it blocks customization.
- Skip it when there is a single class to call, or when the facade would only forward each call one to one.

## Participants in C#
- **Facade** (`UploadService`): a class that knows which subsystem classes handle each request and calls them in order. It adds no new rules of its own.
- **Subsystem classes** (`IVirusScanner`, `IImageCompressor`, `IBlobStorage`, `IMetadataIndex`): do the real work. They do not know about the facade.
- **Client** (`Main`): calls the facade for the common case.

## Example (C#)
A file upload involves scanning, compression, storage and indexing. The facade exposes one method for the common case and takes its subsystem parts from the constructor.

```csharp
using System;
using System.Threading.Tasks;

public interface IVirusScanner
{
    Task<bool> IsCleanAsync(byte[] content);
}

public interface IImageCompressor
{
    byte[] Compress(byte[] content);
}

public interface IBlobStorage
{
    Task<string> PutAsync(string name, byte[] content);
}

public interface IMetadataIndex
{
    Task RegisterAsync(string name, string url, int sizeInBytes);
}

public class UploadService
{
    private readonly IVirusScanner _scanner;
    private readonly IImageCompressor _compressor;
    private readonly IBlobStorage _storage;
    private readonly IMetadataIndex _index;

    public UploadService(IVirusScanner scanner, IImageCompressor compressor, IBlobStorage storage, IMetadataIndex index)
    {
        _scanner = scanner;
        _compressor = compressor;
        _storage = storage;
        _index = index;
    }

    public async Task<string> UploadImageAsync(string name, byte[] content)
    {
        if (!await _scanner.IsCleanAsync(content))
            throw new InvalidOperationException($"{name} failed the virus scan.");
        byte[] small = _compressor.Compress(content);
        string url = await _storage.PutAsync(name, small);
        await _index.RegisterAsync(name, url, small.Length);
        return url;
    }
}

// Small fakes so the example runs.
public class AlwaysCleanScanner : IVirusScanner
{
    public Task<bool> IsCleanAsync(byte[] content) => Task.FromResult(true);
}

public class HalvingCompressor : IImageCompressor
{
    public byte[] Compress(byte[] content) => new byte[content.Length / 2];
}

public class InMemoryStorage : IBlobStorage
{
    public Task<string> PutAsync(string name, byte[] content) => Task.FromResult("memory://" + name);
}

public class ConsoleIndex : IMetadataIndex
{
    public Task RegisterAsync(string name, string url, int sizeInBytes)
    {
        Console.WriteLine($"{name} -> {url} ({sizeInBytes} bytes)");
        return Task.CompletedTask;
    }
}

public static class Program
{
    public static async Task Main()
    {
        var uploads = new UploadService(new AlwaysCleanScanner(), new HalvingCompressor(), new InMemoryStorage(), new ConsoleIndex());
        string url = await uploads.UploadImageAsync("avatar.png", new byte[1024]);
        Console.WriteLine(url);
    }
}
```

## Variations
- **Abstract facade**: make the facade an interface (`IUploadService`) so that clients do not know which subsystem implementation sits behind it, and tests can replace it. An alternative to having several facade classes is to configure one facade with different subsystem objects.
- **Public and private subsystem classes**: the facade is part of the public face, but not the only part. Use `internal` for classes that only the subsystem needs, and leave public the ones that extenders and advanced clients use.
- **Parameterizing the facade**: letting callers pass the scanner or the storage gives flexibility, but each added option takes away from the facade's goal of making the common case simple. Keep the default path short, and offer a second overload or the raw parts for the rare case.
- **One per subsystem layer**: each layer exposes one facade, and layers talk to each other only through facades.

## Risks and C# alternatives
- Keep decisions out of the facade. If it starts choosing storage by customer plan or deciding the retry policy, move that to its own class and let the facade only sequence the calls.
- Watch for a facade that mirrors every method of the subsystem. That is just a renamed API. Offer fewer, task-shaped operations.
- Usually one instance is enough. Register it as a singleton lifetime in the DI container, but do not make it a static global: the container gives the same effect and keeps it replaceable in tests.
- If the operations have no shared state, a static class of helpers is tempting. It makes the subsystem impossible to replace in tests, so prefer an injected instance.

## Related patterns
- [abstract-factory.md](../creational/abstract-factory.md): can create the subsystem objects without naming their concrete classes, or hide platform-specific classes as an alternative to a facade.
- [mediator.md](../behavioral/mediator.md): also abstracts existing classes, but it centralizes communication between peers that know about it, and may add behavior. A facade only simplifies access; the subsystem does not know it exists.
- [singleton.md](../creational/singleton.md): a facade is usually needed only once.
- [adapter.md](adapter.md): an adapter reuses an existing interface, while a facade defines a new one.

## Verification
- A typical client call needs one object and one method, and the client no longer references most subsystem classes.
- Subsystem classes have no reference to the facade.
- Removing the facade would not remove any capability, since advanced clients can still use the parts.
- The facade has tests with fakes that check the order of calls and the failure paths (for example that a failed scan stores nothing).
