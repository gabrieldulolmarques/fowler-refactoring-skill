# Introduce Special Case

Fowler (2018), ch. 10, p. 289. Formerly / aka: Introduce Null Object. Inverse: —.

## When to use
Smells: Temporary Field.
- Many callers of a data structure check for the same special value (null, a sentinel string, a magic id) and most of them respond the same way.
- You want that shared response in one place, so callers just ask the object for what they need.
- Null is the commonest special value, hence the name Null Object, but the technique works for any special case ("unknown", "guest", "no plan").
- Keep a real check where a caller genuinely needs different behavior; a few exceptions are normal.

## Mechanics
Start from a container (class or record) whose property, the subject, can hold the special value, and clients that compare it to that value.

1. Add an `IsSpecialCase`-style property to the subject class, returning `false`.
2. Create the special-case type with only that property, returning `true`.
3. Extract Function ([extract-function.md](../first-set/extract-function.md)) on the special-value comparison, and make every client call the new function instead of comparing directly. Optionally make it throw on unexpected values while you migrate.
4. Make the container return the special-case object instead of the raw special value (or add it through a transform step for plain records).
5. Change the body of the extracted check to use the new property. Compile and test.
6. For each client, find the shared reaction and move it into the special-case type (Combine Functions into Class, [combine-functions-into-class.md](../first-set/combine-functions-into-class.md), or into Transform, [combine-functions-into-transform.md](../first-set/combine-functions-into-transform.md)). Replace the client's conditional with a plain call. Test after each client.
7. Related objects the special case must return are themselves special cases (for example a null history object). Writes that clients used to skip become no-ops on the special case.
8. For clients that still need different behavior, Inline Function ([inline-function.md](../first-set/inline-function.md)) the extracted check into a direct property test.
9. Remove Dead Code ([remove-dead-code.md](../moving-features/remove-dead-code.md)) on the extracted check once nobody calls it.

Treat the special case as a value: it should not change after creation, whatever the real objects it replaces allow. If clients only read, a constant or literal instance can be enough.

## Example
Before: four clients handle a missing customer on an account. The example skips the extracted-check stage (step 3) and goes straight to the final shape.

```csharp
public class Account
{
    private readonly Customer? _customer;
    public Account(Customer? customer) => _customer = customer;
    public Customer? Customer => _customer;
}

public class Customer
{
    public string Name { get; init; } = "";
    public string PlanCode { get; set; } = "";
    public int LateInvoicesLastYear { get; init; }
}

// clients
string label = account.Customer == null ? "guest" : account.Customer.Name;
string plan = account.Customer == null ? "basic" : account.Customer.PlanCode;
if (account.Customer != null) account.Customer.PlanCode = newPlan;
int late = account.Customer == null ? 0 : account.Customer.LateInvoicesLastYear;
```

After: the missing customer is a special-case object.

```csharp
public class Customer
{
    public virtual bool IsMissing => false;
    public virtual string Name { get; init; } = "";
    public virtual string PlanCode { get; set; } = "";
    public virtual int LateInvoicesLastYear { get; init; }
}

public sealed class MissingCustomer : Customer
{
    public override bool IsMissing => true;
    public override string Name { get => "guest"; init { } }
    public override string PlanCode { get => "basic"; set { /* ignored */ } }
    public override int LateInvoicesLastYear { get => 0; init { } }
}

public class Account
{
    private readonly Customer? _customer;
    public Account(Customer? customer) => _customer = customer;
    public Customer Customer => _customer ?? new MissingCustomer();
}

// clients
string label = account.Customer.Name;
string plan = account.Customer.PlanCode;
account.Customer.PlanCode = newPlan;
int late = account.Customer.LateInvoicesLastYear;

// the one client that must behave differently keeps an explicit test
string greeting = account.Customer.IsMissing ? "Welcome, new tenant" : $"Hello, {account.Customer.Name}";
```

Same behavior: callers get the same values as before, and the write to a missing customer is still a no-op.

## C# notes
- With nullable reference types enabled, the special case removes `?` and null checks at the call sites: the property becomes non-nullable and never returns null.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
