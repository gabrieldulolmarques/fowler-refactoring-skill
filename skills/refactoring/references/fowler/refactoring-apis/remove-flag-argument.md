# Remove Flag Argument

Fowler (2018), ch. 11, p. 314. Formerly / aka: formerly Replace Parameter with Explicit Methods. Inverse: —.

## When to use
Smells: Long Parameter List.

A flag argument is a parameter the caller sets to a literal (`true`, an enum member, a string) only to tell the method which branch to run. The call site then says nothing about what the value means, and the list of methods does not show which variations exist.

It is a flag argument only when both hold:
- the caller passes a constant that merely picks a branch, not a value that originates elsewhere in the program;
- the method uses the parameter only to choose a path, not to pass along or store.

Do not change callers that pass computed values. If some callers pass literals and others pass data, add the explicit methods, migrate only the literal callers, and keep the original method for the data callers.

With several independent flags, one method per combination is impractical, so keeping the flags can be reasonable. Treat them as a prompt to split the method into smaller composable ones.

## Mechanics
1. Create one explicit method per value of the parameter, named for what that value means.
   - If the original method already dispatches on the parameter at its outermost level, apply [decompose-conditional.md](../conditional-logic/decompose-conditional.md): each branch becomes the body of an explicit method, and the original just calls them.
   - If the parameter is tangled through the body, make each explicit method a thin wrapper that calls the original with a fixed value.
2. Compile and test.
3. Replace each caller that passes a literal with a call to the matching explicit method. Compile and test after each caller (or small group).
4. When no caller uses the parameter any more, delete the original method. If it stays as a wrapper target, reduce its visibility or rename it so it signals "internal" (for example a `Core` or `Impl` suffix).
5. Compile and test.

## Example
Before:

```csharp
using System.Collections.Generic;

public class Notifier
{
    private readonly List<string> _sent = new();
    private readonly List<string> _queue = new();

    public void Send(string recipient, string text, bool immediate)
    {
        if (immediate)
        {
            _sent.Add(recipient + ": " + text);
            return;
        }
        _queue.Add(recipient + ": " + text);
    }
}

// callers
// notifier.Send("ada@example.com", "Your code is 4821", true);
// notifier.Send("ada@example.com", "Weekly digest", false);
```

After:

```csharp
using System.Collections.Generic;

public class Notifier
{
    private readonly List<string> _sent = new();
    private readonly List<string> _queue = new();

    public void SendNow(string recipient, string text)
    {
        _sent.Add(recipient + ": " + text);
    }

    public void Enqueue(string recipient, string text)
    {
        _queue.Add(recipient + ": " + text);
    }
}

// callers
// notifier.SendNow("ada@example.com", "Your code is 4821");
// notifier.Enqueue("ada@example.com", "Weekly digest");
```

When the flag is used in several places in the body, keep the original and add wrappers instead. In the end state below, the original `Send` has been renamed to `SendCore` and made private, which is possible once no literal caller uses it:

```csharp
using System.Collections.Generic;

public class Notifier
{
    private readonly List<string> _sent = new();
    private readonly List<string> _queue = new();

    public void SendNow(string recipient, string text) => SendCore(recipient, text, immediate: true);
    public void Enqueue(string recipient, string text) => SendCore(recipient, text, immediate: false);

    private void SendCore(string recipient, string text, bool immediate)
    {
        var line = immediate ? "[URGENT] " + text : text;
        if (immediate)
        {
            _sent.Add(recipient + ": " + line);
            return;
        }
        _queue.Add(recipient + ": " + line);
    }
}
```

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Every literal caller now reads as the explicit method, and behavior for each value is unchanged.
