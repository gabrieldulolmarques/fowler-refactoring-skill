# Separate Query from Modifier

Fowler (2018), ch. 11, p. 306. Formerly / aka: -. Inverse: -.

## When to use
Smell: Mutable Data. A function that returns a value and also has observable side effects
is hard to trust: a caller cannot call it freely, repeat it, move it, or test it without
triggering the effect. A function with no observable side effects can be called any number
of times and in any order.

Follow command-query separation: a method that returns a value should not change
observable state, and a method that changes state should not return a computed answer. Split
any method that does both.

Not a violation: a query that updates a private cache for speed. The change is not
observable, since every sequence of calls returns the same results. Leave those alone.

## Mechanics
1. Copy the function and name the copy after what it returns (the query). If its result
   fills a variable at a call site, that variable's name is a good hint.
2. Remove every side effect from the copy, so it only computes and returns the value.
3. Run the compiler or static checks.
4. Find each caller of the original that uses the returned value. Replace the call with a
   call to the query, then add a call to the original below it. Test after each caller.
5. Remove the return value from the original, so it is now a pure command.
6. Test.
7. The query and the command usually duplicate logic now. Remove the duplication, often by
   making the command call the query.

## Example
Before: one method finds the overdue account and suspends it.

```csharp
public record Account(string Id, int DaysOverdue);

public class CollectionsService
{
    private readonly List<string> _suspended = new();

    public string SuspendFirstOverdue(IEnumerable<Account> accounts)
    {
        foreach (var account in accounts)
        {
            if (account.DaysOverdue > 30)
            {
                _suspended.Add(account.Id);
                return account.Id;
            }
        }
        return "";
    }
}

// caller
var id = service.SuspendFirstOverdue(accounts);
Console.WriteLine($"First overdue: {id}");
```

After: a query and a command, with the command reusing the query.

```csharp
public class CollectionsService
{
    private readonly List<string> _suspended = new();

    public string FindFirstOverdue(IEnumerable<Account> accounts)
    {
        foreach (var account in accounts)
        {
            if (account.DaysOverdue > 30) return account.Id;
        }
        return "";
    }

    public void SuspendFirstOverdue(IEnumerable<Account> accounts)
    {
        var id = FindFirstOverdue(accounts);
        if (id != "") _suspended.Add(id);
    }
}

// caller
var id = service.FindFirstOverdue(accounts);
service.SuspendFirstOverdue(accounts);
Console.WriteLine($"First overdue: {id}");
```

Note that the command now runs the search again. That is the usual cost of the split; if
the query is expensive, accept it, cache it invisibly, or pass the found value to the
command instead.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
