# Replace Control Flag with Break

Fowler (2018), web edition only (not in the print book); summary at https://refactoring.com/catalog/replaceControlFlagWithBreak.html. Formerly / aka: Remove Control Flag. Inverse: —.

## When to use
A boolean variable exists only to steer the loop: it is set when something happens, and then
the loop condition or an `if` around the body reads it to skip the remaining work. The reader
has to track the flag across iterations to see when the loop really ends.

Smell: none specific (web edition only).

Replace the flag with a direct exit: `break` to leave the loop. Use `return` when the loop is
at the end of a function (often after Extract Function). `continue` fits only when the flag
guards the rest of a single iteration and not the later ones.
Do not use it when the flag is read after the loop for a real purpose; then it is a result,
not a control flag, and may be better kept or returned from an extracted function.

## Mechanics
1. Consider extracting the code that uses the flag into its own function ([extract-function.md](../first-set/extract-function.md)), so that `return` becomes available as an exit.
2. For each place that sets the flag, replace the assignment with the matching control statement: usually `return` or `break`, and `continue` only when the flag guarded just the rest of one iteration. Before each change, check that nothing between the assignment and the end of the iteration, and nothing after the loop, needs to run once the flag is set. Compile and test after each.
3. When no place sets the flag any more, remove it from the loop condition or the guarding `if`, and delete its declaration. Compile and test.

## Example
Assumes `Customer` and `IMailer` exist.

Before:

```csharp
using System.Collections.Generic;

public void NotifyOverdue(IEnumerable<Customer> customers, IMailer mailer)
{
    bool notified = false;
    foreach (var customer in customers)
    {
        if (!notified)
        {
            if (customer.Balance < 0)
            {
                mailer.SendReminder(customer);
                notified = true;
            }
        }
    }
}
```

After:

```csharp
public void NotifyOverdue(IEnumerable<Customer> customers, IMailer mailer)
{
    foreach (var customer in customers)
    {
        if (customer.Balance < 0)
        {
            mailer.SendReminder(customer);
            break;
        }
    }
}
```

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Behavior is unchanged: the loop still stops at the same element and nothing after the exit point used to run.
