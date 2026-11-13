# Replace Conditional Dispatcher with Command

Kerievsky (2004), ch. 7, p. 191. Pattern: Command. Direction: to, towards.

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
6. In the dispatcher's class, create and fill a command map: a dictionary of command instances keyed by the request identifier. If you have so many commands that registering them is a long list, load them from configuration instead. Compile.
7. Replace the conditional dispatch with a lookup in the map followed by a call to the command's execution method. The class is now the invoker. Compile and test.

## Example
Before: one `switch` does the routing and the work of every handler.

```csharp
using System.Globalization;

public class Payment
{
    public int Id { get; }
    public string Status { get; set; } = "created";
    public string? AuthCode { get; set; }
    public decimal Refunded { get; set; }

    public Payment(int id) { Id = id; }
}

public class PaymentDesk
{
    public string Execute(string command, Payment payment, string[] args)
    {
        switch (command)
        {
            case "authorize":
                payment.AuthCode = args[0];
                payment.Status = "authorized";
                return $"payment {payment.Id} authorized with {payment.AuthCode}";
            case "settle":
                if (payment.Status != "authorized")
                    return $"payment {payment.Id} is not authorized";
                payment.Status = "settled";
                return $"payment {payment.Id} settled";
            case "refund":
                var amount = decimal.Parse(args[0], CultureInfo.InvariantCulture);
                payment.Refunded += amount;
                payment.Status = "refunded";
                return $"payment {payment.Id} refunded {amount}";
            case "receipt":
                return $"receipt for payment {payment.Id}";
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

public interface IPaymentCommand
{
    string Execute(Payment payment, string[] args);
}

public class AuthorizeCommand : IPaymentCommand
{
    public string Execute(Payment payment, string[] args)
    {
        payment.AuthCode = args[0];
        payment.Status = "authorized";
        return $"payment {payment.Id} authorized with {payment.AuthCode}";
    }
}

public class SettleCommand : IPaymentCommand
{
    public string Execute(Payment payment, string[] args)
    {
        if (payment.Status != "authorized")
            return $"payment {payment.Id} is not authorized";
        payment.Status = "settled";
        return $"payment {payment.Id} settled";
    }
}

public class RefundCommand : IPaymentCommand
{
    public string Execute(Payment payment, string[] args)
    {
        var amount = decimal.Parse(args[0], CultureInfo.InvariantCulture);
        payment.Refunded += amount;
        payment.Status = "refunded";
        return $"payment {payment.Id} refunded {amount}";
    }
}

public class ReceiptCommand : IPaymentCommand
{
    public string Execute(Payment payment, string[] args) => $"receipt for payment {payment.Id}";
}

public class PaymentDesk
{
    private readonly Dictionary<string, IPaymentCommand> _commands = new()
    {
        ["authorize"] = new AuthorizeCommand(),
        ["settle"] = new SettleCommand(),
        ["refund"] = new RefundCommand(),
        ["receipt"] = new ReceiptCommand(),
    };

    public void Register(string name, IPaymentCommand command) => _commands[name] = command;

    public string Execute(string command, Payment payment, string[] args) =>
        command != null && _commands.TryGetValue(command, out var handler)
            ? handler.Execute(payment, args)
            : $"unknown command {command}";
}
```

## C# notes
- Where handlers are tiny, a `Dictionary<string, Func<Payment, string[], string>>` is a lighter command type than a class per handler. Switch to classes when a handler needs its own state, dependencies or tests.
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Keep a test for each routed name, one for the unknown name, and (after step 7) one that registers a new command at runtime and runs it.
- Check that no handler kept a reference to the dispatcher's private fields: commands should get what they need through the arguments.
