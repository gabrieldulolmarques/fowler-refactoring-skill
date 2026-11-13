# Replace Constructors with Creation Methods

Kerievsky (2004), ch. 6, p. 57. Pattern: Creation Method. Direction: to.

## When to use
Smells: Duplicated Code, Primitive Obsession.

- A class has several constructors, and callers must read parameter lists or constructor bodies to pick the right one. A call such as `new ClientOptions("https://api.example.com", 30, 1.5)` does not say what kind of client it configures.
- Two kinds of instance need the same parameter types, so the second constructor cannot be written. Named methods have no such limit.
- Constructors nobody calls tend to survive because they are hard to search for. A named creation method is easy to search for, so dead creation code is easier to find and delete.
- A Creation Method is any static or instance method that returns a new instance. Every Factory Method is one, but not the reverse (see [introduce-polymorphic-creation-with-factory-method.md](introduce-polymorphic-creation-with-factory-method.md)).
- Relation to Fowler: [replace-constructor-with-factory-function.md](../../fowler/refactoring-apis/replace-constructor-with-factory-function.md) is the single-constructor version of the same move (one constructor, one named factory). This file is for a class with many constructors: you choose which kinds of instance deserve a name, route them all through one catch-all constructor, and hide the rest.
- Liability: creation becomes nonstandard, because some classes use `new` and others use a Creation Method. If the class has too many constructors because it does too much, apply Extract Class ([extract-class.md](../../fowler/encapsulation/extract-class.md)) first. If most instances use only a small part of its fields, consider splitting it with subclasses. A class that would need dozens of Creation Methods can keep a few public constructors for rare cases, or take parameters in its Creation Methods.
- If the Creation Methods start to crowd out the class's real purpose, move them to a separate factory (the book calls this Extract Factory; see [move-creation-knowledge-to-factory.md](move-creation-knowledge-to-factory.md)).

## Mechanics
1. Find the catch-all constructor, the full-featured one the others delegate to. If there is none, create it with Chain Constructors ([chain-constructors.md](../utilities/chain-constructors.md)).
2. Pick a client that calls a constructor to get one kind of instance. Apply Extract Function ([extract-function.md](../../fowler/first-set/extract-function.md)) on that call to get a public static method, then Move Function ([move-function.md](../../fowler/moving-features/move-function.md)) to put it on the class that owns the constructor. Name it after the kind of instance it returns. Compile and test.
3. Change every other caller of that constructor that wants the same kind of instance to call the Creation Method. Compile and test.
4. If the chosen constructor delegates to another one, make the Creation Method call the delegate directly and inline the chosen constructor (like Inline Function, [inline-function.md](../../fowler/first-set/inline-function.md), applied to a constructor). Compile and test.
5. Repeat steps 2 to 4 for each constructor you want to replace.
6. Make non-public every constructor that has no caller outside the class. Compile.

## Example
Before: four constructors that differ only in which defaults they fill in. Two of them take a single number, so callers must watch the type (`int` or `double`) to get the right one.

```csharp
public class ClientOptions
{
    private readonly string _baseUrl;
    private readonly int _timeoutSeconds;
    private readonly double _backoffFactor;

    public ClientOptions(string baseUrl) : this(baseUrl, 30, 2.0) { }
    public ClientOptions(string baseUrl, int timeoutSeconds) : this(baseUrl, timeoutSeconds, 2.0) { }
    public ClientOptions(string baseUrl, double backoffFactor) : this(baseUrl, 30, backoffFactor) { }
    public ClientOptions(string baseUrl, int timeoutSeconds, double backoffFactor)
    {
        _baseUrl = baseUrl; _timeoutSeconds = timeoutSeconds; _backoffFactor = backoffFactor;
    }

    public string Describe() => $"{_baseUrl} timeout={_timeoutSeconds}s backoff={_backoffFactor}";
}

public static class Caller
{
    public static void Run()
    {
        var a = new ClientOptions("https://api.example.test", 10);
        var b = new ClientOptions("https://api.example.test", 1.5);
    }
}
```

After: only the catch-all constructor remains, private. Each kind of options has a name.

```csharp
public class ClientOptions
{
    private readonly string _baseUrl;
    private readonly int _timeoutSeconds;
    private readonly double _backoffFactor;

    private ClientOptions(string baseUrl, int timeoutSeconds, double backoffFactor)
    {
        _baseUrl = baseUrl; _timeoutSeconds = timeoutSeconds; _backoffFactor = backoffFactor;
    }

    public static ClientOptions Default(string baseUrl) => new(baseUrl, 30, 2.0);
    public static ClientOptions WithTimeout(string baseUrl, int timeoutSeconds) => new(baseUrl, timeoutSeconds, 2.0);
    public static ClientOptions WithBackoff(string baseUrl, double backoffFactor) => new(baseUrl, 30, backoffFactor);

    public string Describe() => $"{_baseUrl} timeout={_timeoutSeconds}s backoff={_backoffFactor}";
}

public static class Caller
{
    public static void Run()
    {
        var a = ClientOptions.WithTimeout("https://api.example.test", 10);
        var b = ClientOptions.WithBackoff("https://api.example.test", 1.5);
    }
}
```

## C# notes
- Optional parameters or object initializers can replace some chained constructors, but they do not name the kind of instance. Use them when the variants differ only by an optional value, and Creation Methods when the variants mean different things.
- A `record` with a private constructor plus static methods works the same way (C# 9+; on Unity it needs an `IsExternalInit` shim).
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- A search for the constructor finds no caller outside the class, and no Creation Method is unused.
- Each Creation Method name says what differs from the default (timeout, backoff), not how the arguments are laid out.
