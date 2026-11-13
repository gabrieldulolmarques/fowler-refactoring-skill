# Replace Conditional Dispatcher with Command

Kerievsky (2004), ch. 7, p. 191. Direction: to, towards. Pattern: Command (GoF, p. 233).

## When to use
Smells: Switch Statements, Large Class, Long Method.

- A conditional dispatcher is a `switch` or `if` chain that routes a request (a command name, a message type, an action code) to the code that handles it. A small one that fits on a screen, with short handlers, is fine as it is.
- Two reasons to move to Command: the set of requests or handlers must be configurable at runtime (the hard-coded `switch` cannot be extended from outside), or the dispatcher and its handlers have grown so large that extracting methods no longer helps because the class is still too big.
- Each handler becomes a command class with one common execution method. A map from request name to command instance replaces the `switch`, and the old class becomes the invoker.
- Command also gives a place to add undo, queuing or logging later, but do not build for that before it is needed: this refactoring is easy to do when the need shows up.
- Liability: it complicates the design when a plain dispatcher was enough.

## Mechanics
1. In the class that holds the dispatcher, take the code that handles one request and apply [extract-function.md](../../fowler/first-set/extract-function.md) until one method runs that behavior: the execution method. Compile and test.
2. Do the same for the remaining requests.
3. Apply [extract-class.md](../../fowler/encapsulation/extract-class.md) to each execution method, so each handler is a class: a concrete command. Its execution method will usually need to be public. If the method is long, apply [compose-method.md](compose-method.md). Compile and test. When all are done, look for duplication among the commands and, if you find it, apply [form-template-method.md](../generalization/form-template-method.md).
4. Define the command type (an interface or abstract class) with the one execution signature all commands share. To choose it, compare the concrete commands:
   - which data must be passed to the common method?
   - which could be given to each command's constructor instead?
   - which could the command fetch by calling back on a parameter?
   - what is the simplest signature that fits all of them?

   You can start by applying [extract-superclass.md](../../fowler/inheritance/extract-superclass.md) or Extract Interface (1st ed. only; no link) to one concrete command. Compile.
5. Make every concrete command implement the command type, and make all client code use them through it. Compile and test.
6. In the dispatcher's class, create and fill a command map: a dictionary of command instances keyed by the request identifier. If you have so many commands that registering them is a long list, load them from configuration instead (the Plugin pattern from Fowler's *Patterns of Enterprise Application Architecture*). Compile.
7. Replace the conditional dispatch with a lookup in the map followed by a call to the command's execution method. The class is now the invoker. Compile and test.

## Example
Before: one `switch` does the routing and the work of every handler.

```csharp
using System.Globalization;

public class Order
{
    public int Id { get; init; }
    public string Status { get; set; } = "new";
    public string? Carrier { get; set; }
    public decimal Refunded { get; set; }
}

public class OrderDesk
{
    public string Execute(string command, Order order, string[] args)
    {
        switch (command)
        {
            case "ship":
                order.Carrier = args[0];
                order.Status = "shipped";
                return $"order {order.Id} shipped with {order.Carrier}";
            case "cancel":
                if (order.Status == "shipped")
                    return $"order {order.Id} already shipped";
                order.Status = "cancelled";
                return $"order {order.Id} cancelled";
            case "refund":
                var amount = decimal.Parse(args[0], CultureInfo.InvariantCulture);
                order.Refunded += amount;
                return $"order {order.Id} refunded {amount}";
            case "invoice":
                return $"invoice for order {order.Id}";
            default:
                return $"unknown command {command}";
        }
    }
}
```

After: every request is a command class, and the desk is an invoker with a map. New commands can be registered at runtime, even from another assembly. The map keeps the old exact-match lookup (change the comparer on purpose, not as a side effect).

```csharp
using System.Collections.Generic;
using System.Globalization;

public class Order
{
    public int Id { get; init; }
    public string Status { get; set; } = "new";
    public string? Carrier { get; set; }
    public decimal Refunded { get; set; }
}

public interface IOrderCommand
{
    string Execute(Order order, string[] args);
}

public class ShipCommand : IOrderCommand
{
    public string Execute(Order order, string[] args)
    {
        order.Carrier = args[0];
        order.Status = "shipped";
        return $"order {order.Id} shipped with {order.Carrier}";
    }
}

public class CancelCommand : IOrderCommand
{
    public string Execute(Order order, string[] args)
    {
        if (order.Status == "shipped")
            return $"order {order.Id} already shipped";
        order.Status = "cancelled";
        return $"order {order.Id} cancelled";
    }
}

public class RefundCommand : IOrderCommand
{
    public string Execute(Order order, string[] args)
    {
        var amount = decimal.Parse(args[0], CultureInfo.InvariantCulture);
        order.Refunded += amount;
        return $"order {order.Id} refunded {amount}";
    }
}

public class InvoiceCommand : IOrderCommand
{
    public string Execute(Order order, string[] args) => $"invoice for order {order.Id}";
}

public class OrderDesk
{
    private readonly Dictionary<string, IOrderCommand> _commands = new()
    {
        ["ship"] = new ShipCommand(),
        ["cancel"] = new CancelCommand(),
        ["refund"] = new RefundCommand(),
        ["invoice"] = new InvoiceCommand(),
    };

    public void Register(string name, IOrderCommand command) => _commands[name] = command;

    public string Execute(string command, Order order, string[] args) =>
        _commands.TryGetValue(command, out var handler)
            ? handler.Execute(order, args)
            : $"unknown command {command}";
}
```

## C# notes
- Where handlers are tiny, a `Dictionary<string, Func<Order, string[], string>>` is a lighter command type than a class per handler. Switch to classes when a handler needs its own state, dependencies or tests.
- With dependency injection, inject `IEnumerable<IOrderCommand>` and let each command expose its name, instead of a long registration list.
- Arguments come in as `string[]` here because the old signature did; a typed request object per command is a later step.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Keep a test for each routed name, one for the unknown name, and (after step 7) one that registers a new command at runtime and runs it.
- Check that no handler kept a reference to the dispatcher's private fields: commands should get what they need through the arguments.
