# Replace Control Flag with Break

Fowler, online catalog: https://refactoring.com/catalog/replaceControlFlagWithBreak.html. Formerly / aka: Remove Control Flag. Inverse: none listed.

## When to use
A boolean variable exists only to steer the loop: it is set when something happens, and then
the loop condition or an `if` around the body reads it to skip the remaining work. The reader
has to track the flag across iterations to see when the loop really ends.

Smells: none in ch. 3 maps to this refactoring (web catalog only).

Replace the flag with a direct exit: `break` to leave the loop. Use `return` when the loop is
at the end of a function (often after Extract Function). `continue` fits only when the flag
guards the rest of a single iteration and not the later ones.
Do not use it when the flag is read after the loop for a real purpose; then it is a result,
not a control flag, and may be better kept or returned from an extracted function.

## Mechanics
The online catalog gives only a before/after example; these steps are a generic derivation.
1. Find the flag: the variable that is set inside the loop and tested to decide whether to keep working or keep looping. Check that nothing after the loop depends on its value.
2. Find the place where the flag is set to its "stop" value.
3. Check what runs between that assignment and the end of the iteration. Make sure none of it needs to run once the flag is set; it will be skipped after the exit. Also check the statements after the loop: none may depend on the loop having run to completion.
4. Put a `break` or `return` right after the assignment; both stop all later iterations. Use `continue` only when the flag was reset on each iteration, so it guarded just the rest of one iteration. Compile and test.
5. Remove the flag from the loop condition or from the `if` that guarded the body. Compile and test.
6. Remove the assignment to the flag and its declaration. Compile and test.

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
