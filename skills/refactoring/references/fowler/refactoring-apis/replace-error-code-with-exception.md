# Replace Error Code with Exception

Fowler (2018), web edition only (not in the print book); summary at https://refactoring.com/catalog/replaceErrorCodeWithException.html. Formerly / aka: —. Inverse: —.
Related: Replace Exception with Precheck ([replace-exception-with-precheck.md](replace-exception-with-precheck.md)).

## When to use
A function reports failure through its return value: a magic number, `null`, `false` or a
status object. Callers must check it after every call, and one that forgets lets the program
continue with bad state. Throwing moves the signal out of the normal return path and lets it
reach whichever layer can handle it.

Use it only for failures that are truly exceptional. If the condition is routine and callers
are expected to branch on it (a lookup that often finds nothing, input that is often invalid),
keep a return-based result or offer a precheck instead; see [replace-exception-with-precheck.md](replace-exception-with-precheck.md).

## Mechanics
1. Add an exception handler higher up the call chain, at the layer that should deal with the
   failure. At first it catches and rethrows everything (`catch { throw; }`), so behavior does
   not change. If a suitable handler already exists, widen it to cover the new path. Compile
   and test.
2. Choose a way to tell the new exceptions apart from all others. In C#, a dedicated exception
   class that carries what the error code carried (a reason, the offending value). Compile.
3. Change the handler so it performs the error action for that exception type and lets every
   other exception propagate. Compile and test.
4. Replace each place that returns the error code with a `throw` of the new exception, one at a
   time. Compile and test after each.
5. When no place returns the code any more, remove the code that checked it and passed it up
   the call stack, testing after each change. A safe way is to first turn each check into a
   trap (`Debug.Fail` or a throw) and delete it once the tests show it never fires. Clear the
   leftovers with [remove-dead-code.md](../moving-features/remove-dead-code.md).
6. If the function's return type existed only to carry the code (an `int` status, a `bool`),
   simplify it, for example to `void`, as a separate step with [change-function-declaration.md](../first-set/change-function-declaration.md).

## Example
Before: `Send` returns a code, and the caller must interpret it.

```csharp
using System;

public class SmsGateway
{
    private int _sentThisMinute;

    public int Send(string phone, string text)
    {
        if (!phone.StartsWith("+")) return -1;      // invalid number
        if (_sentThisMinute >= 100) return -2;      // rate limit exceeded
        _sentThisMinute++;
        return 0;
    }
}

public class NotificationService
{
    private readonly SmsGateway _gateway = new();

    public string Notify(string phone, string text)
    {
        var result = _gateway.Send(phone, text);
        if (result == -1) return "invalid number";
        if (result == -2) return "rate limit exceeded";
        return "sent";
    }
}
```

After: failures are exceptions and the caller handles them where it chooses.

```csharp
using System;

public class DeliveryException : Exception
{
    public DeliveryException(string message) : base(message) { }
}

public class SmsGateway
{
    private int _sentThisMinute;

    public void Send(string phone, string text)
    {
        if (!phone.StartsWith("+"))
            throw new DeliveryException("invalid number");
        if (_sentThisMinute >= 100)
            throw new DeliveryException("rate limit exceeded");
        _sentThisMinute++;
    }
}

public class NotificationService
{
    private readonly SmsGateway _gateway = new();

    public string Notify(string phone, string text)
    {
        try
        {
            _gateway.Send(phone, text);
            return "sent";
        }
        catch (DeliveryException e)
        {
            return e.Message;
        }
    }
}
```

## C# notes
- Do not use exceptions for expected control flow: they are slow compared with a branch and
  hide the normal paths of the program. Reserve them for failures the caller cannot reasonably
  avoid by checking first.
- Prefer a specific exception type (or a built-in one such as `ArgumentException` or
  `InvalidOperationException` where it fits) over a bare `Exception`, and catch the narrowest type.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Add a test per former error code that asserts the exception is thrown with the right data.
- Search for callers outside the solution (reflection, other assemblies) that still expect the code.
