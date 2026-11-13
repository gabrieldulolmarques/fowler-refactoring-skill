# Command

Gamma et al. (1995), ch. 5, p. 233. Also known as: Action, Transaction. Category: object behavioral.

## Intent
Turn a request into an object. That lets you pass requests around as values, parameterize callers with them, queue or log them, and undo them.

## When it pays off
- An object must trigger an action without knowing what it does or on whom (buttons, menu items, schedulers, job queues). A command object replaces the callback.
- Requests must be queued, run later, logged, replayed after a crash, or sent to another process.
- You need undo and redo: the command keeps what it needs to reverse itself, and a history list gives multiple levels.
- The system is organized around high-level operations built from primitive ones, as in transaction-based information systems: a command encapsulates a set of changes to data, and all commands share one interface.
- Benefits: the invoker is decoupled from the receiver, commands are first-class objects, they compose into macros, and new commands need no change to existing classes.
- Liability: one class per action can be heavy. For a simple callback that needs no undo or data, a delegate is enough.

## Participants in C#
- **Command** (`ICartCommand`): interface with `Execute` and, if undo is supported, `Undo`.
- **ConcreteCommand** (`AddItemCommand`, `ApplyCouponCommand`, `MacroCommand`): binds a receiver to an action, stores the arguments and the data needed to undo.
- **Receiver** (`Cart`): knows how to do the real work.
- **Invoker** (`CartHistory`): runs commands and keeps the history for undo and redo.
- **Client** (`Program`): creates the concrete commands and hands them to the invoker.

## Example (C#)
An online checkout cart whose changes can be undone. The invoker stores executed commands on a stack; each command captures what it needs to reverse itself.

```csharp
using System;
using System.Collections.Generic;

public class Cart
{
    private readonly Dictionary<string, int> _quantities = new();

    public string? Coupon { get; set; }

    public int QuantityOf(string sku) => _quantities.TryGetValue(sku, out var q) ? q : 0;

    public void SetQuantity(string sku, int quantity)
    {
        if (quantity <= 0) _quantities.Remove(sku);
        else _quantities[sku] = quantity;
    }
}

public interface ICartCommand
{
    void Execute();
    void Undo();
}

public class AddItemCommand : ICartCommand
{
    private readonly Cart _cart;
    private readonly string _sku;
    private readonly int _amount;
    private int _previous;

    public AddItemCommand(Cart cart, string sku, int amount)
    {
        _cart = cart;
        _sku = sku;
        _amount = amount;
    }

    public void Execute()
    {
        _previous = _cart.QuantityOf(_sku);   // state needed to reverse exactly
        _cart.SetQuantity(_sku, _previous + _amount);
    }

    public void Undo() => _cart.SetQuantity(_sku, _previous);
}

public class ApplyCouponCommand : ICartCommand
{
    private readonly Cart _cart;
    private readonly string _code;
    private string? _previous;

    public ApplyCouponCommand(Cart cart, string code)
    {
        _cart = cart;
        _code = code;
    }

    public void Execute()
    {
        _previous = _cart.Coupon;
        _cart.Coupon = _code;
    }

    public void Undo() => _cart.Coupon = _previous;
}

public class MacroCommand : ICartCommand
{
    private readonly List<ICartCommand> _commands;

    public MacroCommand(IEnumerable<ICartCommand> commands) => _commands = new List<ICartCommand>(commands);

    public void Execute()
    {
        foreach (var command in _commands) command.Execute();
    }

    public void Undo()
    {
        for (int i = _commands.Count - 1; i >= 0; i--) _commands[i].Undo(); // reverse order
    }
}

public class CartHistory
{
    private readonly Stack<ICartCommand> _done = new();
    private readonly Stack<ICartCommand> _undone = new();

    public void Run(ICartCommand command)
    {
        command.Execute();
        _done.Push(command);
        _undone.Clear();   // a new action invalidates the redo branch
    }

    public void Undo()
    {
        if (_done.Count == 0) return;
        var command = _done.Pop();
        command.Undo();
        _undone.Push(command);
    }

    public void Redo()
    {
        if (_undone.Count == 0) return;
        var command = _undone.Pop();
        command.Execute();
        _done.Push(command);
    }
}

public static class Program
{
    public static void Main()
    {
        var cart = new Cart();
        var history = new CartHistory();

        history.Run(new AddItemCommand(cart, "sku-1", 2));
        history.Run(new MacroCommand(new ICartCommand[]
        {
            new AddItemCommand(cart, "sku-2", 1),
            new ApplyCouponCommand(cart, "WELCOME10"),
        }));

        history.Undo();   // removes sku-2 and the coupon together
        Console.WriteLine($"{cart.QuantityOf("sku-1")} {cart.QuantityOf("sku-2")} {cart.Coupon ?? "none"}");
    }
}
```

## Variations
- **How smart the command is.** At one end it only binds a receiver to a call. At the other it does the whole job itself, with no receiver, which suits actions that fit no existing class.
- **Undo and redo.** The command stores the receiver, the arguments and the receiver's previous values. One level needs only the last command; several levels need a history list whose maximum length is the number of levels.
- **Copy before storing.** If one command object is reused for many invocations and its state differs each time, store a copy in the history, not the shared object. If its state never changes after execution, keep the reference.
- **Avoiding drift.** Repeated undo and redo can accumulate small errors. Store the exact previous state (a snapshot) instead of recomputing a reverse operation when exactness matters.
- **Macro commands.** A composite of commands. Its undo must run the parts in reverse order.
- **Logging for recovery.** Commands that can be serialized can be written to a log and re-executed after a failure.

## Risks and C# alternatives
- If there is no undo and no data to carry, a delegate (`Action`, `Func<Task>`) is the command. Use a class only when you need state, undo, naming or serialization.
- A command that stores a snapshot rather than a delta uses more memory. Cap the history length.
- Commands in a queue that run later may see a receiver in a different state. Make them check preconditions in `Execute`.
- `async` commands: return `Task` from `ExecuteAsync` and decide what undo means if the action already left the process (an e-mail cannot be unsent; model a compensating command).
- Request/handler libraries that dispatch `IRequest` objects to handlers apply the same idea, with the handler as the receiver.

## Related patterns
- [Composite](../structural/composite.md): implements macro commands.
- [Memento](memento.md): keeps the state a command needs to undo its effect.
- [Prototype](../creational/prototype.md): a command that must be copied before entering the history list acts as a prototype.
- [Chain of Responsibility](chain-of-responsibility.md): commands are often the requests that travel along a chain.

## Verification
- Executing and then undoing a command leaves the receiver exactly as before, for each command and for a macro.
- The invoker compiles without references to concrete commands or receivers.
- Undo after redo after undo returns to a consistent state (no drift).
- Adding a new action means adding one class and no edit to the invoker or the history.
