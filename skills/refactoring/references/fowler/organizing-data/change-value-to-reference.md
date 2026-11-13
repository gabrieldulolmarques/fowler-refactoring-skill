# Change Value to Reference

Fowler (2018), ch. 9, p. 256. Formerly / aka: —. Inverse: Change Reference to Value
([change-reference-to-value.md](change-reference-to-value.md)).

## When to use
- Several host objects (invoices, orders) each hold their own copy of the same logical entity
  (one account, one customer), built with `new` from the same identifier.
- The entity is updated or enriched over time, so every copy must be found and changed. A missed
  copy leaves the data inconsistent.
- The entity has a real identity: two objects with the same id are the same thing, not just
  equal values.

Not worth it when the entity is never updated: copies are then harmless, and a value is simpler
(no repository, no lifetime to manage). Duplicate memory alone is rarely a reason.

## Mechanics
1. Create a repository (or registry) that holds one instance per identifier, if the code does not
   have one yet. Reuse an existing one when there is one.
2. Make sure the code that builds the host object has what it needs to look up the right
   instance, usually the identifier already present in its input.
3. Change the host's constructor (or the code that creates it) to ask the repository for the
   instance instead of calling `new`. Compile and test after each constructor you change.
4. Decide how the repository is filled: created on first request, or pre-loaded so that an
   unknown id is an error. Make the host's behavior match that choice.
5. If the repository is a global, consider passing it in as a constructor parameter so the host
   is not coupled to shared state.

## Example
Before: every invoice builds its own `Account`, so two invoices for the same account hold two
separate objects.

```csharp
public class Account
{
    public Account(string id) { Id = id; }
    public string Id { get; }
    public decimal CreditLimit { get; set; }
}

public class Invoice
{
    public Invoice(string number, string accountId)
    {
        Number = number;
        Account = new Account(accountId);
    }

    public string Number { get; }
    public Account Account { get; }
}
```

Raising the credit limit through one invoice does not affect the other.

After: a repository hands out one `Account` per id, and `Invoice` uses it.

```csharp
using System.Collections.Generic;

public class AccountRepository
{
    private readonly Dictionary<string, Account> _accounts = new();

    public Account GetOrRegister(string id)
    {
        if (!_accounts.TryGetValue(id, out var account))
        {
            account = new Account(id);
            _accounts[id] = account;
        }
        return account;
    }

    public Account? Find(string id) =>
        _accounts.TryGetValue(id, out var account) ? account : null;
}

public class Invoice
{
    public Invoice(string number, string accountId, AccountRepository accounts)
    {
        Number = number;
        Account = accounts.GetOrRegister(accountId);
    }

    public string Number { get; }
    public Account Account { get; }
}
```

Now `a.Account` and `b.Account` are the same object for the same id, so a change made through one
invoice is seen by all. Here the repository is passed in rather than read from a global.

## C# notes
- A repository or registry that hands out the shared instance is the usual shape: a
  dictionary keyed by id, behind a small class.
- If the repository is shared across threads, use a thread-safe structure (for example
  `ConcurrentDictionary.GetOrAdd`) so two callers cannot create two instances for one id.
- Reference equality is the default for a class, which is what you want here: do not add value
  equality to the shared entity.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Add a test that two hosts built from the same id return the same instance
  (`Assert.Same`), and that a change made through one is visible through the other.
