# Move Creation Knowledge to Factory

Kerievsky (2004), ch. 6, p. 68. Pattern: Factory. Direction: to.

## When to use
Smells: Solution Sprawl.

- The data and code needed to build one kind of object are spread over several classes. The book calls this creation sprawl. It usually starts when a client wants to configure an object but cannot reach the code that creates it, so it hands its preferences to one object, which hands them to another, until some distant class finally uses them.
- A Factory gathers both the creation logic and the preferences in one class. The client sets up the factory once, and the same factory instance later does the creation wherever it is needed.
- The book's definition: any class that has one or more Creation Methods is a Factory, static or not, returning an interface, an abstract class or a concrete class. A Factory Method is a different thing, a polymorphic method in a hierarchy. An Abstract Factory is a Factory that can be swapped at run time to build a family of related objects. If the Factory's creation logic grows too complex, it can evolve into one.
- A Factory can be a class or an interface implemented by an existing class. The interface form is useful when other code should talk to that class only through its creation role.
- Liability: a Factory adds a class. If every object in the system is created through a factory, there are too many. Do not add one only to hide a choice between two concrete classes in one place. It has to remove sprawl or allow a configuration that plain `new` cannot.

## Mechanics
These steps assume the Factory is a class. An interface needs small changes.
1. The *instantiator* is the class that collaborates with others to create the *product*. Make sure it creates the product through a Creation Method ([replace-constructors-with-creation-methods.md](replace-constructors-with-creation-methods.md)), changing the product class if needed. Compile and test.
2. Create the factory class, named after what it creates (`OrderFactory`). Compile.
3. Move the Creation Method to the factory with Move Function ([move-function.md](../../fowler/moving-features/move-function.md)). If it was static, make it an instance method now. Compile.
4. Make the instantiator create the factory and call it to get the product. Repeat for every instantiator that stopped compiling. Compile and test.
5. Look for data and methods in the other classes that exist only to feed the creation. Move them into the factory with Move Field ([move-field.md](../../fowler/moving-features/move-field.md)) and Move Function, which may also change who creates the factory. Compile and test after each move.

## Example
Before: `ApiSession` knows the request options, passes them to `RequestSender`, which only copies them onto the request it creates. Both classes carry the same two fields.

```csharp
public class ApiRequest
{
    public string Path { get; }
    public ApiRequest(string path) { Path = path; }
    public int TimeoutSeconds { get; set; }
    public int MaxRetries { get; set; }
}

public class ApiSession
{
    private readonly int _timeoutSeconds;
    private readonly int _maxRetries;
    public ApiSession(int timeoutSeconds, int maxRetries) { _timeoutSeconds = timeoutSeconds; _maxRetries = maxRetries; }
    public ApiRequest Send(string path) => new RequestSender(_timeoutSeconds, _maxRetries).Prepare(path);
}

public class RequestSender
{
    private readonly int _timeoutSeconds;
    private readonly int _maxRetries;
    public RequestSender(int timeoutSeconds, int maxRetries) { _timeoutSeconds = timeoutSeconds; _maxRetries = maxRetries; }
    public ApiRequest Prepare(string path) => new ApiRequest(path) { TimeoutSeconds = _timeoutSeconds, MaxRetries = _maxRetries };
}
```

After: `RequestFactory` holds the options and builds the request. The session configures it once. The sender no longer knows what the options are.

```csharp
public class RequestFactory
{
    private readonly int _timeoutSeconds;
    private readonly int _maxRetries;
    public RequestFactory(int timeoutSeconds, int maxRetries) { _timeoutSeconds = timeoutSeconds; _maxRetries = maxRetries; }
    public ApiRequest CreateRequest(string path) => new(path) { TimeoutSeconds = _timeoutSeconds, MaxRetries = _maxRetries };
}

public class ApiSession
{
    private readonly RequestFactory _factory;
    public ApiSession(int timeoutSeconds, int maxRetries) { _factory = new RequestFactory(timeoutSeconds, maxRetries); }
    public ApiRequest Send(string path, RequestSender sender) => sender.Prepare(path, _factory);
}

public class RequestSender
{
    public ApiRequest Prepare(string path, RequestFactory factory) => factory.CreateRequest(path);
}
```

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The options now live in one class. A search for the fields that used to be copied between classes finds only the factory.
- The factory removes real sprawl. If it only wraps a single `new`, undo it.
