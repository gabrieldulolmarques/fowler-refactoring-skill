# Move Creation Knowledge to Factory

Kerievsky (2004), ch. 6, p. 68. Direction: to. Pattern: Factory (not in GoF).

## When to use
Smells: Solution Sprawl.

- The data and code needed to build one kind of object are spread over several classes. The book calls this creation sprawl. It usually starts when a client wants to configure an object but cannot reach the code that creates it, so it hands its preferences to one object, which hands them to another, until some distant class finally uses them.
- A Factory gathers both the creation logic and the preferences in one class. The client sets up the factory once, and the same factory instance later does the creation wherever it is needed.
- The book's definition: any class that has one or more Creation Methods is a Factory, static or not, returning an interface, an abstract class or a concrete class. A Factory Method (GoF) is a different thing, a polymorphic method in a hierarchy. An Abstract Factory is a Factory that can be swapped at run time to build a family of related objects. If the Factory's creation logic grows too complex, it can evolve into one.
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
Before: `CheckoutPage` knows the order options, passes them to `CheckoutService`, which only copies them onto the order it creates. Both classes carry the same two fields.

```csharp
public class Order
{
    public string Customer { get; }
    public Order(string customer) { Customer = customer; }
    public string? Note { get; set; }
    public bool Express { get; set; }
}

public class CheckoutPage
{
    private readonly bool _express;
    private readonly string _note;
    public CheckoutPage(bool express, string note) { _express = express; _note = note; }
    public Order Submit(string customer) => new CheckoutService(_express, _note).Place(customer);
}

public class CheckoutService
{
    private readonly bool _express;
    private readonly string _note;
    public CheckoutService(bool express, string note) { _express = express; _note = note; }
    public Order Place(string customer) => new Order(customer) { Note = _note, Express = _express };
}
```

After: `OrderFactory` holds the options and builds the order. The page configures it once. The service no longer knows what the options are.

```csharp
public class OrderFactory
{
    private readonly bool _express;
    private readonly string _note;
    public OrderFactory(bool express, string note) { _express = express; _note = note; }
    public Order CreateOrder(string customer) => new(customer) { Note = _note, Express = _express };
}

public class CheckoutPage
{
    private readonly OrderFactory _factory;
    public CheckoutPage(bool express, string note) { _factory = new OrderFactory(express, note); }
    public Order Submit(string customer, CheckoutService service) => service.Place(customer, _factory);
}

public class CheckoutService
{
    public Order Place(string customer, OrderFactory factory) => factory.CreateOrder(customer);
}
```

## C# notes
- If other code should depend only on the creation role, extract an interface (`IOrderFactory`) and let the class implement it.
- With dependency injection, the factory is often registered as a service. The refactoring is still the same: move the knowledge first, then decide how the factory is supplied.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The options now live in one class. A search for the fields that used to be copied between classes finds only the factory.
- The factory removes real sprawl. If it only wraps a single `new`, undo it.
