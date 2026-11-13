# Remove Middle Man

Fowler (2018), ch. 7, p. 192. Formerly / aka: —. Inverse: Hide Delegate ([hide-delegate.md](hide-delegate.md)).

## When to use
Smell: Middle Man. A class hides a delegate behind forwarding methods, and over time most of
its members do nothing except call the same member on the delegate. Each new delegate feature
forces another forwarder, and the class adds no behavior of its own.

Typical trigger: hiding applied too eagerly, in the name of "never talk to strangers". How much
to hide is a judgment call that changes as the system evolves, so it is fine to reverse an
earlier Hide Delegate.

Not a reason to remove everything: a few forwarders that clients use constantly can stay. It is
also fine to keep the hiding where the delegate is likely to be replaced or its structure is
likely to change, since callers would then be shielded from that change.

## Mechanics
1. Add a getter (an accessor) on the server that exposes the delegate object.
2. Pick one forwarding method. In each client that calls it, replace the call with a chained
   call through the new accessor (`server.Delegate.Member`). Compile and test after each
   replacement.
3. When no caller of that forwarding method is left, delete it. Compile and test.
4. Repeat steps 2 and 3 for the other forwarders you want to remove.

If your tooling supports it, a shortcut is to apply Encapsulate Variable to the delegate field
so the forwarders go through the public accessor, then Inline Function on each forwarder to
replace all its callers at once ([encapsulate-variable.md](../first-set/encapsulate-variable.md), [inline-function.md](../first-set/inline-function.md)).

## Example
Before: `Workspace` hides its `BillingAccount` and forwards to it.

```csharp
public class BillingAccount
{
    public string BillingEmail { get; }
    public decimal CreditBalance { get; }

    public BillingAccount(string billingEmail, decimal creditBalance)
    {
        BillingEmail = billingEmail;
        CreditBalance = creditBalance;
    }
}

public class Workspace
{
    private readonly BillingAccount _billingAccount;

    public Workspace(BillingAccount billingAccount) => _billingAccount = billingAccount;

    public string BillingEmail => _billingAccount.BillingEmail;
    public decimal CreditBalance => _billingAccount.CreditBalance;
}

public static class Client
{
    public static string Email(Workspace workspace)
    {
        string email = workspace.BillingEmail;
        return email;
    }
}
```

Step 1: expose the delegate.

```csharp
public class Workspace
{
    private readonly BillingAccount _billingAccount;

    public Workspace(BillingAccount billingAccount) => _billingAccount = billingAccount;

    public BillingAccount BillingAccount => _billingAccount;
    public string BillingEmail => _billingAccount.BillingEmail;
    public decimal CreditBalance => _billingAccount.CreditBalance;
}
```

Steps 2 and 3: update each client, then delete the forwarders that are no longer used.

```csharp
public class Workspace
{
    public Workspace(BillingAccount billingAccount) => BillingAccount = billingAccount;

    public BillingAccount BillingAccount { get; }
}

public static class Client
{
    public static string Email(Workspace workspace)
    {
        string email = workspace.BillingAccount.BillingEmail;
        return email;
    }
}
```

Behavior is the same; `Workspace` no longer needs a new member each time `BillingAccount` gains one.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
