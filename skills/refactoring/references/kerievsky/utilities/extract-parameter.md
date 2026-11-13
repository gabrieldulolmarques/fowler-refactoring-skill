# Extract Parameter

Kerievsky (2004), ch. 11, p. 346. Pattern: —. Direction: —.

## When to use
Smells: — (a low-level step; the book needed it right after turning inheritance into delegation).

- A field is assigned from an object created inside the class (in a constructor or method), and you would rather let the client decide which object it gets.
- Split the assignment in two: the client supplies the right-hand side, the class keeps the left-hand side.
- The book used it in [move-embellishment-to-decorator.md](../simplification/move-embellishment-to-decorator.md), after Replace Superclass with Delegate ([replace-superclass-with-delegate.md](../../fowler/inheritance/replace-superclass-with-delegate.md)): the class that delegates created its own delegate, but a client needed to supply it.

## Mechanics
1. The assignment must be in a constructor or method. If it is not (a field initializer, for example), move it into one first.
2. Add a parameter for the value ([change-function-declaration.md](../../fowler/first-set/change-function-declaration.md)), typed as the field's type. Pass at each call site the expression that used to sit in the assignment, and change the assignment to use the parameter. Compile and test.
3. If the old arguments of the method are no longer used, remove them with Change Function Declaration too.

## Example
Before: the uploader creates its own cool-tier store, so uploading to another tier means editing the class.

```csharp
public interface IBlobStore { string Put(string key, byte[] data, string contentType); }

public class CoolBlobStore : IBlobStore
{
    public string Put(string key, byte[] data, string contentType) => $"cool/{key}";
}

public class Uploader
{
    private readonly IBlobStore _store;

    public Uploader() => _store = new CoolBlobStore();

    public string Upload(string key, byte[] data) => _store.Put(key, data, "application/octet-stream");
}
```

After: the store comes from the client. The old behavior lives in the call site that builds the uploader.

```csharp
public class Uploader
{
    private readonly IBlobStore _store;

    public Uploader(IBlobStore store) => _store = store;

    public string Upload(string key, byte[] data) => _store.Put(key, data, "application/octet-stream");
}

public static class Caller
{
    public static Uploader Make() => new(new CoolBlobStore());
}
```

## C# notes
- Validate at the boundary: a `null` parameter should fail with `ArgumentNullException.ThrowIfNull(store)` where a null would otherwise show up much later.
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- No code in the class creates the value any more, and a test can now pass in a fake of the type.
